var http = require('http');
var exec = require('child_process').exec;
const qs = require('querystring');
const normalizeUrl = (url) => {
    if(url.indexOf('?') !== -1) {
        return url.replace( /\/\?/g, '' );
    }
    return url;
};

//create a server object:
http.createServer(function (req, res) {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  if(req.url!="/favicon.ico") {
     console.log( qs.parse(normalizeUrl(req.url)).city);
     var objToJson = { };
     objToJson.response = res;
     exec('python3 /root/git-projects/pymeteoam/alexa.py \'' + qs.parse(normalizeUrl(req.url)).city + '\'', function callback(error, stdout, stderr){
        res.write(JSON.stringify({weather: stdout.slice(0, -1)})); //write a response to the client
        res.end(); //end the response
     });
  }
}).listen(3012); //the server object listens on port 3010
