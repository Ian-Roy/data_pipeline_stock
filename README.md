you will need to provide an api key from alpha vantage you can sign up free here https://www.alphavantage.co/

once you have a key put it in the config file `data_pipes/config.py`

this set up depends on docker and docker compose 

to build run `docker-compose build`

then `docker-compose up -d`

to run this you will first need to set up the couch db database. i have created a init script to run it attach to the master scheduler and run the init.py python file `python init.py`

after running the init file you can run the pipeline by attaching to the master scheduler container and running `python get_historic_moving_avg.py`

you can view the cluster at `localhost:8787/status`

the script will store charts in base 64 strings in the couch db as a notification type doc you can verify these images using any number of base 64 decoding tools. here is an example in python

img_out=base64.decodebytes(base64_string)
with open('test.png', 'wb') as f:
    f.write(img_out)