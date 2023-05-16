# A minimal CORS server

Makes a request to the given url on the server and returns the text content.

### How To Use:
Make a post request to `https://<YOUR-ENDPOINT>/<target-url?>` with a body in the following format:
```ts
{
  method: string,
  url?: string,
  body?: string,
  headers?: dict,
  data?: dict,
  cache?: bool,
  max_age?: number
}
```
`target-url`: If the `url` is not set in the body, this one will be used to make the request.

`method`: The request method to use when making the request on the server. This can be one of `GET`, `POST`, `PUT` or `DELETE`.

`url`: The url to make a request to. Can be `None` if the `target-url` is set. 

`body`: The body to append to the request when fetching the response.

`headesr`: The headers to use when fetching the response.

`data`: The form data to use when fetching the response.

`cache`: If set to `true`, a cached response will be returned if available and new requests will be cached.

`max_age`: The time in second how long a cached response should be valid. If unset or `0` the cache won't invalidate.

#### Note
Either the `target-url` parameter in the URL or the `url` in the body must be set. If both are present, the url from the body will be used.



