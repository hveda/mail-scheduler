Mail Scheduler
=================

An example of automated mail sender using Flask-Mail and asynchronous job scheduling with RQ.

## Setup

### Configuration
Rename .env.example to .env
And then set your variable there.

Quickly run the project using [docker](https://www.docker.com/) and
[docker-compose](https://docs.docker.com/compose/):
```bash
docker-compose up -d
```

Create the database tables:
```bash
docker-compose run --rm app flask create_db
```

### Asynchronous job scheduling with RQ

`RQ` is a [simple job queue](http://python-rq.org/) for python backed by
[redis](https://redis.io/).

Start a worker:
```bash
flask rq worker
```

Start a scheduler:
```bash
flask rq scheduler
```

Monitor the status of the queue:
```bash
flask rq info --interval 3
```

For help on all available commands:
```bash
flask rq --help
```

## How to use

Go to http://0.0.0.0:5000/api/doc

Or you can run in your terminal
```bash
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{ \ 
   "subject": "Email subject", \ 
   "content": "Email body", \ 
   "timestamp": "07 Feb 2018 00:06 +08", \ 
   "recipients": "user1%40mail.com, user2%40mail.com" \ 
 }' 'http://127.0.0.1:5000/api/save_emails'
 ```