from flask import Flask, request, render_template,jsonify,redirect
from flask_cors import CORS,cross_origin
from bs4 import BeautifulSoup as bs
import requests
import logging
import os
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/results",methods=['GET','POST'])
def scrape_imageResults():
    image_data_mongo=[]
    images_address=[]
    if request.method=='POST':
        try :
            search_query=request.form['query'].replace(" ","")
            query_name=request.form['query']
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
            response=requests.get(f"https://www.google.com/search?q={search_query}&sxsrf=AJOqlzX-9p-NpMWhZGIvlO7ksJBnCBKe7w:1679061819881&source=lnms&tbm=isch&sa=X&ved=2ahUKEwj9vtHakOP9AhVXSWwGHTN_CF0Q0pQJegQIBRAE&biw=1366&bih=649&dpr=1")
            save_directory='images/'

            if not os.path.exists(save_directory):
                os.makedirs(save_directory)
            
            images_document=bs(response.content,'html.parser')
            image_tags=images_document.find_all("img",{"class":"yWs4tf"})

            for index,image in enumerate(image_tags):
                image_url=image['src']
                image_data=requests.get(image_url).content
                myDict={'index':image_url,'image':image_data}
                image_data_mongo.append(myDict)

                with open(os.path.join(save_directory,f"{search_query}_{image_tags.index(image)}.jpg"),"wb") as f:
                    f.write(image_data)
                images_address.append(image_url)
            

            client = pymongo.MongoClient("mongodb+srv://pwskills:pwskills@cluster0.nj6x4ec.mongodb.net/?retryWrites=true&w=majority")
            db =    client['image_scrapper']
            image_coll=db['image_scrape_data']
            image_coll.insert_many(image_data_mongo)
            
            return render_template('results.html',images_address=images_address,title=query_name)

        except Exception as e:
            logging.info(e)
            return "something is wrong ."
    
    else:
            return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0",debug=True)
