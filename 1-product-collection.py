#!/usr/bin/python
# -*-coding:UTF-8 -*-

# https://bitbucket.org/basti/python-amazon-product-api
import amazonproduct
# https://github.com/ligyxy/MySQLTool
from DictMySQLdb import DictMySQLdb
import random
import time


class IdCache:
    def __init__(self, con):
        """
        Pass in the mysql connection from mysqltool
        :param con: DB()
        """
        self.con = con
        self.cache = {}

    def __call__(self, tablename, value):
        keys = '_'.join([tablename.lower()] + [str(k).lower() + '_' + str(v).lower() for k, v in value.iteritems()])

        if self.cache.get(keys):
            return self.cache.get(keys)
        else:
            id_db = self.con.get(tablename, value)
            self.cache[keys] = id_db
            return id_db


pd_db = DictMySQLdb(user='root', passwd='', host='127.0.0.1', db='product')
cache = IdCache(pd_db)

api = amazonproduct.API(locale='us')
# Initialize the starting keywords
keywordlist = ['watch', 'Amazonbasic', 'large', 'cushion', 'pad', 'bag', 'man', 'women', 'kid', 'rocket', 'pet', 'car',
               'office', 'face', 'leg', 'home', 'cleaning', 'food', 'fruit', 'outdoor', 'indoor', 'usa', 'china',
               'business', 'TV', 'key', 'rome', 'english', 'map', 'math', 'computer', 'kitchen', 'pet', 'Gift',
               'Beauty', 'Philips', 'Appliances', 'Accessories', 'american']
keyword = random.sample(keywordlist, 1)[0]
count = 0


def get_cat_id(pd_asin):
    try:
        nodes = api.item_lookup(pd_asin, ResponseGroup='BrowseNodes')
        nodeid = nodes.Items.Item.BrowseNodes.BrowseNode.BrowseNodeId
        node = api.browse_node_lookup(nodeid).BrowseNodes
    except amazonproduct.errors.InvalidParameterValue:
        return None
    # Get the root category
    cat_list = []
    while True:
        try:
            name = node.BrowseNode.Name
            node = node.BrowseNode.Ancestors
            if node is not None:
                cat_list.append(name)
        except AttributeError:
            try:
                # The last category is the root cat
                pd_root_cat = node.BrowseNode.Name
                cat_list.append(pd_root_cat)
                # Root cats' upper_level is 1
                level = 1
                for cat in cat_list[::-1]:
                    level = cache('category', {'name': cat, 'upper_level': level})
                return {'root': cache('category', {'name': pd_root_cat, 'upper_level': 1}),
                        'leaf': level}
            except Exception:
                return None
while True:
    result = []
    value_list = []
    # Assume the similar search will return product in same root category
    root_cat_list = {}
    leaf_cat_list = {}
    try:
        for item in api.item_search('All', Keywords=keyword):
            pd_asin = unicode(item.ASIN)
            pd_title = unicode(item.ItemAttributes.Title)
            pd_cat = unicode(item.ItemAttributes.ProductGroup)
            result.append(pd_asin)
            if pd_asin and pd_title and pd_cat:
                # pd_root_cat_id & pd_leaf_cat_id is the cache for categories with their ids
                # We assume the leaf categories are unique
                if root_cat_list.get(pd_cat) and leaf_cat_list.get(pd_cat):
                    pd_root_cat_id = root_cat_list.get(pd_cat)
                    pd_leaf_cat_id = leaf_cat_list.get(pd_cat)
                    print 'Get ids from cache'
                # If not in cache, get the id through browsenode API and store them into cache
                else:
                    cat_id = get_cat_id(pd_asin)
                    if cat_id:
                        pd_root_cat_id = cat_id.get('root')
                        pd_leaf_cat_id = cat_id.get('leaf')
                        root_cat_list[pd_cat] = pd_root_cat_id
                        leaf_cat_list[pd_cat] = pd_leaf_cat_id
                        print 'Get ids through API'
                    # Skip it if no category id returns
                    else:
                        print 'Cannot get root category'
                        continue
                if pd_root_cat_id and pd_leaf_cat_id:
                    value_list.append((pd_asin, pd_title, pd_leaf_cat_id, pd_root_cat_id))
        if value_list:
            # asin is UNIQUE in database
            pd_db.cur.executemany('INSERT IGNORE INTO item (asin, title, category_id, root_category_id) VALUES (%s, %s, %s, %s)',
                                  value_list)
            pd_db.conn.commit()
            print 'Insert a new list! length: %d\n' % len(value_list)
        if len(result) > 5:
            try:
                pick = random.sample(result, 2)
                # Pick two product randomly to perform similarity searching
                title = api.similarity_lookup(pick[0], pick[1], SimilarityType='Random').Items.Item.ItemAttributes.Title
                keyword = ' '.join(unicode(title).split(' ')[-2::])
            except amazonproduct.errors.NoSimilarityForASIN:
                keyword = random.sample(keywordlist, 1)[0]
        else:
            keyword = random.sample(keywordlist, 1)[0]
    except Exception:
        # The API and the package are not rubust enough
        del api
        api = amazonproduct.API(locale='us')
        print 'TIMEOUT ERROR'
        time.sleep(100)
    count += 1


pd_db.close()