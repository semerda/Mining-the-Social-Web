# -*- coding: utf-8 -*-

import sys
import couchdb
from jwzthreading import thread, Message
from CouchDBBulkReader import CouchDBBulkReader
from datetime import datetime as dt
try:
    import jsonlib2 as json
except:
    import json

DB = sys.argv[1]
NUM_THREADS = 3

# Pull the data as efficient as possible from CouchDB by using a thread
# pool to get as close as possible to being I/O bound.
# A single request to _all_docs works except that it CPU bound to a single core

now = dt.now()
print 'Bulk reading from CouchDB...'
br = CouchDBBulkReader(DB, NUM_THREADS)
docs = br.read()
print '\t%s' % (dt.now() - now, )

now = dt.now()
print 'Threading in Memory...'
threads = thread([Message(doc) for doc in docs])
print '\t%s' % (dt.now() - now, )

# Write out threading info into another database.
# Note that writes to CouchDB are serialized to append-only
# databases, so threading is unlikely to help here, and besides,
# the average document size is very small, making this a quick operation

now = dt.now()
print 'Bulk writing to CouchDB...'
server = couchdb.Server('http://localhost:5984')
db = server.create(DB + '-threads')
results = db.update([{'thread': thread} for thread in threads],
                    all_or_nothing=True)
print '\t%s' % (dt.now() - now, )

# Some basic stats

print 'Total number of threads: %s' % len(threads)
print

# Compute (_id, len(thread)) tuples

stats = sorted(zip([result[1] for result in results], [len(t) for t in threads]),
               key=lambda x: x[1])
print 'Thread Id'.ljust(40), 'Thread Length'.rjust(20)
print '-' * 80
for stat in stats:
    print stat[0].ljust(40), str(stat[1]).rjust(20)

# You could also compute thread length directly in CouchDB using a simple reducer function