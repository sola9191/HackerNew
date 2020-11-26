import requests
from flask import Flask, render_template, request

base_url = "http://hn.algolia.com/api/v1"

# This URL gets the newest stories.
new = f"{base_url}/search_by_date?tags=story"

# This URL gets the most popular stories
popular = f"{base_url}/search?tags=story"



# This function makes the URL to get the detail of a storie by id.
# Heres the documentation: https://hn.algolia.com/api
def make_detail_url(id):
  return f"{base_url}/items/{id}"  



db = {}
app = Flask("DayNine")

@app.route("/<id>")
def get_id(id):
  comment_list = []
  info = {}
  url = make_detail_url(id)
  request_url = requests.get(url)
  result = request_url.json()
  title = result["title"]
  url = result["url"]
  author = result["author"]
  points = result["points"]
  info={
    "title": title,
    "url": url,
    "author": author,
    "points": points,
  }
  children = result["children"]
  for child in children:
    text = child["text"]
    author = child["author"]
    if author==None:
      comment_list.append(
        {
          "text" : "[deleted]"
        }
      )
    else:
      comment_list.append(
        {
          "text" : text,
          "author" : author
        }
      )
  return render_template("detail.html", info=info, lists=comment_list)
 

def get_detail(hit):
  
  title = hit["title"]
  url = hit["url"]
  author = hit["author"]
  points = hit["points"]
  comment = hit["num_comments"]
  ob_id = hit["objectID"]

  return {
    "title": title,
    "url": url,
    "author": author,
    "points": points,
    "comment": comment,
    "id": ob_id
  }

@app.route("/")
def home():
  
  order = request.args.get("order_by") #/?order_by =
  if order: #/?order_by=xxx 가 있으면
    
    if order=="new": #orer_by=new 면
      existing_new_list = db.get("new") #db에 저장되있는지확인후
      if existing_new_list:  #db에 있을경우
        lists = existing_new_list
      else: #db에 없을경우
        lists = get_newslist(new)  #function을 통해 값을 구한다.
        db["new"] = lists #db에도 저장
      return render_template("index.html", lists=lists)
    
    elif order=="popular": 
      existing_pop_list = db.get("pop")
      if existing_pop_list:
        lists = existing_pop_list
      else:
        lists = get_newslist(popular)
        db["pop"] = lists
      return render_template("index.html", lists=lists)
  
  else:
    existing_pop_list = db.get("pop")
    if existing_pop_list:
      lists = existing_pop_list
    else:
      lists = get_newslist(popular)
      db["pop"] = lists
    return render_template("index.html", lists=lists)
  
def get_newslist(word):
  lists = []
  request_url = requests.get(word)
  result = request_url.json()
  hits = result.get("hits")

  for hit in hits:
    lists.append(get_detail(hit))  
  return lists
 
app.run(host="0.0.0.0")
