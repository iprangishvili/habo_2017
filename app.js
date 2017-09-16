var express = require('express'),
  bodyParser = require('body-parser'),
  methodOverride = require('method-override'),
  fs = require('fs'),
  http = require('http'),
  path = require('path');


var PythonShell = require('python-shell');
var options = {
  mode: 'text',
  pythonPath: 'python',
  pythonOptions: ['-u'],
  scriptPath: ""
};
var app = module.exports = express();

/**
 * Configuration
 */

// all environments
app.set('port', process.env.PORT || 3000);
app.use('/', express.static(__dirname + '/'));
app.use(bodyParser.json());
/**
 * Routes
 */
app.get('/',function(req,res){
  res.redirect('/Sample.html');
});

app.post('/command',function(req, res){
  var result = req.body
  console.log(result.DisplayText)
  options.args = [result.DisplayText]
  PythonShell.run('main.py', options, function (err, results) {
    if (err) console.log(err)
    console.log("no error")
    console.log(results)
  });
});
// serve index and view partials

/**
 * Start Server
 */

http.createServer(app).listen(app.get('port'), function () {
  console.log('Express server listening on port ' + app.get('port'));
});
