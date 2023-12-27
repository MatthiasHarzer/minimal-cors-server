# A minimal CORS server

Makes a request to the given url on the server and returns the text content. Optionaly caches the response for improved response-time.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## How to setup
- Copy the [`docker-compose.yml`](./docker-compose.yml) file into your local directory.
- Run `docker compose up -d` to start the container.
- The server should now run on `0.0.0.0:9999` (you can change the port in the `docker-compose.yml` file)

### Configure caching behavior (optional)
You can configure the caching behavior of the server by setting some environment variables in the [`docker-compose.yml`](./docker-compose.yml) file.
There are four caching modes available by setting the `CACHE_MODE` environment variable:

| **`CACHE_MODE`**     | Description                                                                         | Additional settings                                                                                                                                                                                                                                                                    |
|----------------------|-------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `sqlite` _(default)_ | Saves the responses in a SQLite database                                            | Set the `SQLITE_FILE` environment variable to modify the cache file. Defaults to `./cache.db`.<br> __Note:__ You can use this in combination with a [docker compose volume](https://docs.docker.com/compose/compose-file/07-volumes/) to make the database file available on the host. |
| `mysql`              | Connects to a MySQL-database to cache responses                                     | Requires setting `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD` and `MYSQL_DATABASE` environment variables accordingly. `MYSQL_PORT` can be used if the MySQL server is running on a non-standard port.                                                                                  |
| `memory`             | Uses an in-memory cache to store responses                                          | _(none)_                                                                                                                                                                                                                                                                               |
| `none`               | Disables caching completely. `cache` and `max_age` will be ignored for all requests | _(none)_                                                                                                                                                                                                                                                                               |

If an unrecognized value is set for `CACHE_MODE`, no caching will be used.
See the [`examples`](./examples) for some example docker compose configurations.
 
## Update the Docker image
- Run `docker compose down` to stop the running container
- Rebuild the image with `docker compose build --no-cache`
- Start the container with `docker compose up -d`

You can also use the very simple [`rebuild.sh`](./rebuild.sh) script to update the server.

## How To Use
Make a `POST` request to `https://<YOUR-ENDPOINT>/` with a body in the following format:
```ts
{
  method: string,
  url: string,
  body?: string,
  headers?: dict,
  data?: dict,
  cache?: bool,
  max_age?: number
}
```
`method`: The request method to use when making the request on the server. This can be one of `GET`, `POST`, `PUT` or `DELETE`.

`url`: The url to make a request to. 

`body`: The body to append to the request when fetching the response.

`headesr`: The headers to use when fetching the response.

`data`: The form data to use when fetching the response.

`cache`: If set to `true`, a cached response will be returned if available and new requests will be cached.

`max_age`: The time in second how long a cached response should be valid. If unset or `0` the cache won't invalidate.

