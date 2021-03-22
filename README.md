# REST API for a bid server

The goal of this repository is to build a REST API for a bid server. These are the requirements:

* record a user’s bid on an item;
* get the current winning bid for an item;
* get all the bids for an item;
* get all the items on which a user has bid;
* build simple REST API to manage bids;

## 1. Technology

We'll use the following technologies:

* Django framework
* Django REST framework to build the API
* Postgres database
* Docker compose file to run the API and the Postgres database
* JWT tokens for API authentication
* Postman collection with sample requests
* Automatic tests for the API
* Management commands to create test data

## 2. Data structures and concurrency

### 2.1 Data structures

We define two tables/models where the information will be saved.

* Item: Will contain the item name and description, plus the best bid so far for that item.
* Bid: Will contain the item, user, date (created and last updated), and the bid amount.

In order to be efficient when calculating the best bid for an item, every time a bid is done/updated, we will check if is the best bid for the item, and will save it in the item best_bid field.
This will allow us to retrieve the best bid together with the item information.

Some constraints we added:

* Once an item has a best bid, only new bids with higher amount will be allowed. Other lower amounts will result in a HTTP 400 error.
* A user can't have more than a bid per item.
* The item API is a read only API, items can be created using a django management command (see below).

### 2.2 Users and permissions
The API uses JWT tokens for authentication. You can retrieve a new access token sending a POST to the endpoint:

```
POST http://localhost:8000/api/token/
{
    "username": "user2@bids.com",
    "password": "1234password2"
}
```

Every request needs an Authentication header, with a content like:

```
Bearer <the access token retrieved in authentication>
```

For testing purposes, the JWT tokens have an expiration time of 15 days.

Some constraints we added related to permissions:

* There are regular users and super users (django auth `is_staff` field set to true).
* A regular user can see and operate only on his/her own bids.
* The item best_bid is visible for all users.
* Items are accessible for all users.
* A super user can see and operate on all bids.

### 2.3 Concurrency
We rely on Postgres transactions for concurrency. 
Every time a bid is created or updated, the item owning the bid will be used to create a lock, with a `select_for_update()`.
This ensures that there won't be two concurrent bids on the same item.


## 3. Instructions to run and test

### 3.1 Run the server
To start the server, run `docker-compose up` in the root folder. You'll need docker installed in your machine.

### 3.2 Run the tests
To run the automatic tests, once the server is running, execute:

```
docker exec -it bidapi python manage.py test
```

There are tests for models, serializers and views, covering all the requirements.

### 3.3 Create items

The item API is a read only API (that was not a requirement). In order to create a new item, you can insert it in the database directly, or execute a management command:

```
docker exec -it bidapi python manage.py create_item "item name" "item description"
```

### 3.4 Create test data

There's a management command that allows to create some test data, useful for testing with Postman.

```
docker exec -it bidapi python manage.py create_test_data
```

This command deletes all existing data in the database.

### 3.5 Create users

There's no API for users (was not a requirement), so if you want to create more users, you can do it programmatically (see the `create_test_data` command), or using the django admin interface (you'll need a super user for that, use `createsuperuser` django command to create it) 

### 3.6 Tests with postman

There's a postman collection in the root folder containing requests for items, bids and authentication.
