# Foodgram web-app


## Description
Cooking blog web-app. Create recipes, find other recipes by tags or ingredients, add favourites and form shopping lists.

## Deployment

In infra folder create containers in detached mode  
```
docker-compose up -d
```
<br />

enter backend container terminal  
```
docker exec -it <web_container_id> /bin/bash
```
<br />

make migrations and create superuser  
```
python manage.py migrate
python manage.py createsuperuser
```
<br />

add ingredients to database using “loadjson” command  
```
python manage.py loadjson
```
<br />

create some tags via admin panel  
http://localhost/admin/

You’re good to go, open it at http://localhost/
