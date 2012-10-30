var version = "v20121030-1223";

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
    replicaset = nconf.get('replicaset'),
    database = nconf.get('database'),
    sensorsin = nconf.get('sensors');

var sensorname = {}
var isensin = sensorsin.length-1;
do {
    sensorname[sensorsin[isensin].dbid] = sensorsin[isensin].name
} while( isensin-- );
// Only load enabled sensors
var sensors = [];
for (var i = 0; i < sensorsin.length; i++) {
    if (sensorsin[i].enabled) {
	sensors.push(sensorsin[i]);
    }
}

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

var db = mongoose.createConnection(mongos, database, mongooptions);

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
      hostname: os.hostname(),
      sensors: sensors
  });
});

var senddata = function(err, readings, res) {
    if (!err) {
        res.contentType('application/json');
	res.send({"result": "OK", "readings": readings});
    } else {
        res.contentType('application/json');
        res.send('{"result": "error reading database"}');
        console.log(err);
    };
};

app.get('/readings', function(req, res) {
    var sincedate = req.query['sincedate'],
        tilldate = req.query['tilldate'],
        limit = req.query['limit']
    ;
    if (!limit) {
        limit = 10000;
    }
    Reading.find({}).where('date').gt(sincedate).lte(tilldate).limit(limit).sort({'date': 1})
	.exec(function(err, reading) { senddata(err, reading, res); });
});

app.get('/export', function(req, res) {
  res.render('export.ejs', {
      layout: false,
      version: version,
      hostname: os.hostname(),
      sensorlist: sensorname
  });
});

// Start the app
var port = process.env.PORT || 5000;
server.listen(port, function() {
  console.log("Listening on " + port);
});
