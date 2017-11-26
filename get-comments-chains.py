import json, requests, csv
import datetime

#get a subreddit, get all the latest posts.

def getSubredditThreads(subreddit, amountOfThreads):
	limit = 100
	if amountOfThreads < limit:
		limit = amountOfThreads
	results = []
	keydict = {}
	count = 1
	afterCode = ''
	while len(results) < amountOfThreads:
		print 'getting page ', count
		count = count + 1
		
		
		baseurl = 'https://www.reddit.com/r/' + subreddit + '/new/.json'
		params = {}
		params['limit'] = amountOfThreads
		params['after'] = afterCode
	
		r = requests.get(baseurl, params = params, headers = {'User-agent': 'chainBot 0.1'})
	
		data = r.json()
		afterCode = data['data']['after']
		print 'new after code: ', afterCode
		
		for comment in data['data']['children']:
			commentdata = {}
			commentdata['subreddit'] = subreddit
			commentdata['thread'] = comment['data']['id']
			#print comment['data']['created']
			#check if duplicated
			if commentdata['thread'] not in keydict:
				keydict[commentdata['thread']] = True;
				print datetime.datetime.fromtimestamp(comment['data']['created'])
				print json.dumps(commentdata, indent=4, sort_keys=True)
				results.append(commentdata)
			else:
				print 'duplicate: ', commentdata['thread']
		print 'results ', len(results)
	
	#print json.dumps(data, indent=4, sort_keys=True)
	
	return results

# get all the comments for one thread

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
	
	

threads = getSubredditThreads('italy', 900)
edges = {}

for thread in threads:
	tdata = getThreadComments(thread['subreddit'], thread['thread'], edges)
	
#save results in csv

ofile  = open('results.csv', "wb")
writer = csv.writer(ofile, delimiter='\t', quotechar='"')
writer.writerow(['Source','Target','Weight'])

for sourceName in edges:
	source = edges[sourceName]
	for targetName in source:
		value = source[targetName]
		print 'adding ', sourceName, targetName, value
		writer.writerow([sourceName,targetName,value])

	
#print json.dumps(edges, indent=4, sort_keys=True)


