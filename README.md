# SBUX

This project streams "Starbucks" filtered [Twitter](https://twitter.com/) tweets and generates a word cloud. Future updates to the project will provide additional functionality and analysis of this data.

### Components

A Python producer is used to connect to the Twitter firehose and sends the data to a RabbitMQ queue. A Python consumer reads from the queue and saves the data into a Postgres database. A Node.js API will read from the database and push the data to a ReactJS frontend app using socket.io.