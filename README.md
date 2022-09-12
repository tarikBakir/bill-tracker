# Bill Tracker

## Table of contents
* [General info](#general-info)
* [Database diagram](#database-diagram)
* [Class diagram](#class-diagram)
* [Sequence diagram](#sequence-diagram)
* [Technologies](#technologies)
* [Setup](#setup)
* [Deployment](#deployment)

## General info
I decided on developing a **bill tracker** web application that will have the
following features:
* **Log bills, amounts and date**: 
A user will be able to log upcoming household bills manually, and
probably using X company’s API which will provide the upcoming bill of
the month for the user and so the user does not need to input it
manually.
* **List bills**: 
The user will be able to list and sort all his bills by different factors; such
as date/amount/company.
* **Have a few graphs (this year / last year)**: 
A graph for the user to show analytical data about the bills in terms of
amounts or even the different categories of the bills.
* **Store them somewhere**: 
The user data will be available on a cloud database so the user will be
able to view the data from anywhere.

* **Authentication**:
There are many excellent Python authentication packages, but none of them do every‐
thing. The user authentication solution presented in this chapter uses several packages
and provides the glue that makes them work well together. This is the list of packages
that will be used:
* Flask-Login: Management of user sessions for logged-in users
* Werkzeug: Password hashing and verification
* itsdangerous: Cryptographically secure token generation and verification
In addition to authentication-specific packages, the following general-purpose exten‐
sions will be used:
* Flask-Mail: Sending of authentication-related emails
* Flask-Bootstrap: HTML templates
* Flask-WTF: Web forms



## Database diagram
 ![](bill-tracker-DB_diagram.drawio.png)   
## Class diagram
![](class-diagram-bill-tracker.drawio.png)
## Sequence diagram
![](bill-tracker-Sequence Diagram.drawio.png)
## Technologies
Project is created with:
* Flask version: 2.2.2
* Jinja2 version: 3.1.2
* SQLAlchemy version: 1.4.41
* Flask-Bootstrap: 2.2.1 
* JQuery: 2.0.x
	
## Setup
To run this project, follow the steps [here](https://phoenixnap.com/kb/install-flask)

## Deployment
Deployment of the project will be done through azure web services.
Steps for the deployment found [here](https://docs.microsoft.com/en-us/azure/app-service/quickstart-python?tabs=flask%2Cwindows%2Cazure-cli%2Cvscode-deploy%2Cdeploy-instructions-azportal%2Cterminal-bash%2Cdeploy-instructions-zip-azcli)

**Tarik Bakir , ID:207426255**
