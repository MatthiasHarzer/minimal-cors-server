# A minimal CORS server

Makes a request to the given url on the server and returns the text content.

### Use:
Make a post request to `https://<YOUR-ENDPOINT>/request` with a body in the following format:
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
where `method` is one of `GET`, `POST`, `PUT` or `DELETE`. The `url` is the url you want to make a request to. If `cache` is set to `True`, a cached response is returned if available. `max_age` indicates how many seconds a cached response should be saved until refetching; if not provided, `max_age` will be `0`, indicating no limit. 
