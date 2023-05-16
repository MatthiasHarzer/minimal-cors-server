# A minimal CORS server

Makes a request to the given url on the server and returns the text content.

### How To Use:
Make a post request to `https://<YOUR-ENDPOINT>/` with a body in the following format:
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

