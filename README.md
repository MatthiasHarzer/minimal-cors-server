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
  cache?: bool
}
```
where `method` is one of `GET`, `POST`, `PUT` or `DELETE`. The `url` is the url you want to make a request to. If `cache` is set to `True`, a cached response is returned if available. 
