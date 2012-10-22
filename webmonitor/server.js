var version = "v20121022-1729";

// Import and setup
var express = require('express'),
    uuid = require('node-uuid'),
    util = require('util'),
    ejs = require('ejs'),
    underscore = require('underscore'),
    nconf = require('nconf'),
    io = require('socket.io'),
    mongoose = require('mongoose'),
    http = require('http'),
    connect = require('connect'),
    os = require('os')
    ;

// Read configuration
nconf.file({ file: 'monitor.json' });
var mongos = nconf.get('mongos'),
    replicaset = nconf.get('replicaset');

var mongooptions = {
        'db': {
            'native_parser': true
        },
        'server': {
            'auto_reconnect': true,
            'poolSize': 10
        },
        'replset': {
            'readPreference': 'nearest',
            'strategy': 'ping',
            'rs_name': replicaset,
            'slaveok': true
        }
    };

var db = mongoose.createConnection(mongos, 'baking', mongooptions);

var readingSchema = new mongoose.Schema({
  type:  String,
  id: String,
  date: { type: Date, default: Date.now },
  error: String,
  reading: {
    value: Number,
    unit:  String
  }
});

var app = express();
app.use(express.bodyParser());
app.use(express.static(__dirname + '/public'));
app.use(connect.compress());
var server = http.createServer(app)

var io = require('socket.io').listen(server);

var Reading = db.model('readings', readingSchema);
Reading.findOne({ }, function (err, reading) {
    if ((!err) && (reading)) {
	console.log('%s: %s %s', reading.id, reading.reading.value, reading.reading.unit);
    } else {
	console.log("Error-sadface!");
    }
});

// Main page
app.get('/', function(req, res) {
  res.render('index.ejs', {
      layout: false,
      version: version,
      hostname: os.hostname()
  });
});


app.get('/readings', function(req, res) {
    var sincedate = req.query['sincedate'],
        tilldate = req.query['tilldate'];
    Reading.find({}).where('date').lt(sincedate).gt(tilldate).sort({'date': 1})
	.exec(function(err, readings) { 
            if (!err) {
              res.contentType('application/json');
		res.send({"result": "OK", "readings": readings});
            } else {
              res.contentType('application/json');
              res.send('{"result": "error reading database"}');
              console.log(err);
            }
        });
});

// Start the app
var port = process.env.PORT || 5000;
server.listen(port, function() {
  console.log("Listening on " + port);
});
