# spaces-backup-worker
A worker listening to a RabbitMQ queue to save/delete file from filesystem if they are deleted from spaces

Digital Ocean spaces are not reliable if as reported by some users (e.g. https://medium.com/@nodegin/i-lose-all-my-data-by-using-digitalocean-spaces-247888cc05ae).
As we have to use this in production we decided to keep a backup of all files that we save in spaces to filesystem as well. We have written a microservice that will CRUD the files in spaces and once operation on spaces is done it will send a message to a RabbitMQ queue which this worker will be listening to.

## Configuration
Set following Environment valriables on docker host:
```
export DO_ACCESS_KEY_ID=XXXXX
export DO_SECRET_ACCESS_KEY=XXXX
```

Update following environment variables based on your spaces setup in docker-compose.yaml:
```
      - S3_REGION_NAME=ams3
      - S3_ENDPOINT_URI=https://ams3.digitaloceanspaces.com
      - S3_BUCKET_NAME=swat1
```

Change other settings in docker-compose.yaml as required.

## Running the app
Use docker-compose to bring up the app. It will start rwo container - one for RabbitMQ and one for worker.
```
docker-compose up --build
```

## Test
Open RabbitMQ Management at http://localhost:8080 > Queues > Publish Message

### Backup File
```
{
	"operation":"DOWNLOAD",
	"file_name": "TestDownload.xlsx"
}
```
### Delete File
```
{
	"operation":"DELETE",
	"file_name": "TestDownload.xlsx"
}
```