# Restful raffle

## Getting started
```

python3.9 -m venv env
source env/bin/activate
pip install -r requirements.txt
export MANAGER_IPS=123.123.123.123,127.0.0.2
pytest




MANAGER_IPS=['123.123.123.123','127.0.0.1']

Endpoint documentation can be found on the: {base url of the project}/docs/ and can be tested  
(Example: http://localhost:8000/docs)
```

## Task

Fix the failing tests by writing a raffle application in Python that provides a REST API.

Make modifications to the project structure and existing files (including `testing/*.py`) as needed. The project has been initialized as an empty Django project with Django REST framework to get you going. You can remove those or start from scratch, if you prefer something else. However, you must incorporate `testing/*.py` in your project to validate the raffle behavior. The application is ready when the tests pass and rules and requirements listed below are followed.

Update the "Getting started" instructions above, if additional steps or changes are needed to run the tests. Update also the "API endponts" table below, if changes are made.

When you are done, package the project directory as a zip file excluding external libraries - using the included `package.sh` might be helpful. Submit your zip according to instructions given separately.

## Rules and requirements

* The raffle manager creates a new raffle specifying the number of tickets and the prizes.
* Ticket numbers for each raffle are sequential starting from `1`. I.e. if a raffle has 50 tickets total, the ticket numbers must be `1, 2, ..., 49, 50`.
* The raffle tickets are be given out to participants requesting them in a non-sequential order.
* The raffle tickets contain a verification code, that can be used to validate the ticket (e.g. when redeeming prizes).
* The application does not save the verification codes in plaintext.
* The same ticket number is never given out to multiple participants of a raffle.
* One ip address may not participate in a raffle more than once.
* When no raffle tickets are remaining, the raffle manager draws the winners.
* The winners must not be pre-determined.
* One raffle ticket can't win more than one prize.
* Access to the raffle manager endpoints is only allowed from ips listed in the `MANAGER_IPS` environment variable.
* The application performance should not severly degrade with a large number of raffle tickets, prizes and participants.

## API endpoints

| Endpoint                            | Description                               | Manager only |
|-------------------------------------|-------------------------------------------|:------------:|
| `POST /raffles/`                    | Create a new raffle                       |     Yes      |
| `GET /raffles/`                     | List raffles starting from latest         |      No      |
| `GET /raffles/<id>/`                | Get details of a raffle                   |      No      |
| `POST /raffles/<id>/participate/`   | Get a raffle ticket                       |      No      |
| `POST /raffles/<id>/winners/`       | Draw winners of a raffle                  |     Yes      |
| `GET /raffles/<id>/winners/`        | List winners of a raffle                  |      No      |
| `POST /raffles/<id>/verify-ticket/` | Verify ticket and winnings                |      No      |