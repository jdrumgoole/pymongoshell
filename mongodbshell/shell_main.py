import argparse

from mongodbshell import Client

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--uri", default="mongodb://localhost:27017/test",
                        help="URI for connecting to MongoDB, [default: %(default)s]")
    parser.add_argument("--database",
                        default="test",
                        help="Database to connect to, default: %(default)s]")
    parser.add_argument("--collection",
                        default="test",
                        help="collection to connect to, default: %(default)s]")

    args = parser.parse_args()
    proxy = Client(database_name=args.database,
                   collection_name=args.collection,
                   mongodb_uri=args.uri)
    client = proxy.client
    db = proxy.database
    collection = proxy.collection
    find = proxy.find

    banner = ('\n'
              'The MongoDB Python Shell, use the \'proxy\' object as a wrapper for the client.\n'
              'We also have wrapper objects for the follow objects:\n'
              '\n'
              'client      : proxy.client\n'
              'database    : proxy.database\n'
              'collection  : proxy.collection\n'
              'find        : proxy.find\n'
              '    ')
    print(banner)
    print(proxy)
