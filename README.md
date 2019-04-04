# spaces-backup-worker
A worker listening to a RabbitMQ queue to save/delete file from filesystem if they are deleted from spaces

Digital Ocean spaces are not reliable if as reported by some users (e.g. https://medium.com/@nodegin/i-lose-all-my-data-by-using-digitalocean-spaces-247888cc05ae).
As we have to use this in production we decided to keep a backup of all files that we save in spaces to filesystem as well. We have written a microservice that will CRUD the files in spaces and once operation on spaces is done it will send a message to a RabbitMQ queue which this worker will be listening to.
