import json, requests, csv
import datetime


def getThreadComments(subreddit, threadname, results):
	
	#call the main api
	baseurl = 'https://www.reddit.com/r/' + subreddit + '/comments/' + threadname + '/.json'
	print baseurl
	params = {}
	r = requests.get(baseurl, params = params, headers = {'User-agent': 'chainBot 0.1'})
	
	data = r.json()
	

	replies = data[1]['data']['children']
	
	for reply in replies:
		#check if it contains a thread of replies
		if reply['kind'] == 't1':
			#get the author
			author = reply['data']['author']
			
			if 'prev_author' in reply:
				#save it in the results
				#print '  ', author,' > ', reply['prev_author']
				#check if source exists
				if reply['prev_author'] not in results:
					results[reply['prev_author']] = {}
				#check if target exists
				if author not in results[reply['prev_author']]:
					results[reply['prev_author']][author] = 0
				#increase the edge value
				results[reply['prev_author']][author] = results[reply['prev_author']][author] + 1
				
			else:
				#print ' root ', author
				True
			#check if the comment has childrens
			if reply['data']['replies'] != "":
				#get childrens, add to list.
				for child in reply['data']['replies']['data']['children']:
					child['prev_author'] = author
					#if the object has kind: "t1" it means that there are comments
					#if the object has kind: "more" it means that there are just codes
					if child['kind'] == "t1":
						replies.append(child)
						#print '  added +1 to ', author
					elif child['kind'] == "more":
						print ' more comments'
						print json.dumps(child, indent=4, sort_keys=True)
						# still to understand how to get 'more' comments
						# see https://www.reddit.com/r/redditdev/comments/67mdxm/how_to_use_apimorechildren/
						# this is another example https://www.reddit.com/api/morechildren.json?api_type=json&link_id=t3_7fk5mw&children=dqcshyh
						
					else:
						print ' other kind'
						print json.dumps(child, indent=4, sort_keys=True)
		else:
			#TODO do something with more
			print 'more comments not parsed'
		
def getMoreComments(threadId, childId):
	baseurl = 'https://www.reddit.com/api/morechildren.json?api_type=json'
	params = {}
	params['link_id'] = threadId
	params['children'] = childId
	r = requests.get(baseurl, params = params, headers = {'User-agent': 'chainBot 0.1'})
	data = r.json()
	#rebuild the tree out of the comments
	

#load ids from csv
threads = []
errors = []

with open('data/r-italy-posts-from-bigquery.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    headers = readCSV.next()
    for row in readCSV:
    	threads.append(row[1])

#threads = getSubredditThreads('italy', 100)
print json.dumps(threads, indent=4, sort_keys=True)
edges = {}

count = 0

for thread in threads:
	count = count + 1
	print count, '/', len(threads)
	print thread
	try:
		tdata = getThreadComments('italy', thread, edges)
	except:
		print 'ERRORE'
		errors.append([thread])
	
#save results in csv

ofile  = open('results.csv', "wb")
writer = csv.writer(ofile, delimiter='\t', quotechar='"')
writer.writerow(['Source','Target','Weight'])

for sourceName in edges:
	source = edges[sourceName]
	for targetName in source:
		value = source[targetName]
		print 'adding ', sourceName, targetName, value
		if(value > 1):
			writer.writerow([sourceName,targetName,value])

ofile  = open('errors.csv', "wb")
writer = csv.writer(ofile, delimiter='\t', quotechar='"')
writer.writerow(['thread','error'])

#save errors in csv
for err in errors:
	writer.writerow[err]
	
#print json.dumps(edges, indent=4, sort_keys=True)


