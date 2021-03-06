<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>BOMon {{ version }} on {{ hostname }}</title>
  <link href="/static/css/jquery-ui.css" rel="stylesheet" type="text/css">
  <style type="text/less">

   @cw: 600px;
   @rh: 200px;
   @roff: 400px;

   #chamberdiv {
     position:absolute;
     top:0;
     left:0;
     width:1361px;
   }

%for i in range(len(sensors)):
   #{{ sensors[i]['dbid'] }}div {
     position:absolute;
     top: {{ sensors[i]['labelpos'][0]}};
     left: {{ sensors[i]['labelpos'][1]}};
     width:150px;
   }
%end

%for i in range(len(sensors)):
   #{{ sensors[i]['dbid'] }}cdiv {
     position:absolute;
     top: @rh * {{ sensors[i]['plotpos'][0]}} + @roff;
     left: @cw * {{ sensors[i]['plotpos'][1] }};
   }
%end

  .showvals {
   font-family: monospace;
  }

label {
 display:block;
 font-family: monospace;
}

input {
 font-family: monospace;
 font-weight: bold;
 size: 4;
 border: 3px solid white;
}

.warning {
 border: 3px solid red;
}

#messages {
  position: absolute;
  top: 0;
  left: 1450;
}

#messagebox {
  width: 300;
  height: 300;
}

#spanselect {
  position: absolute;
  top: 320;
  left: 1450;
  width: 300;
}

#loading {
  position: absolute;
  top: 375;
  left: 1450;
  font-family: monospace;
  display: block;
  font-size: 16;
  background: #EE8888;
  width: 300;
}

.hidden {
  visibility: hidden;
}

#time {
  position: absolute;
  top: 10;
  left: 10;
  font-family: monospace;
  font-weight: bold;
  font-size: 25;
  border: 1px dotted black;
  padding: 2px;
}

#timestamp {
  position: absolute;
  top: 47;
  left: 10;
  font-family: monospace;
  font-weight: bold;
  font-size: 10;
  border: 1px dotted green;
  padding: 2px;
}

#links {
  position: absolute;
  top: 10;
  left: 150;
  font-family: monospace;
  font-weight: bold;
  font-size: 10;
  border: 1px solid black;
  padding: 2px;
}

.pressurediv {
 border: 1px solid black;
 width: 150px;
 padding: 3px;
}

.stale {
 outline: 3px solid #E09004;
}

   </style>

    <script language="javascript" type="text/javascript" src="/static/js/libs/jquery-1.8.2.min.js"></script>
    <script src="/static/js/libs/jquery-ui-1.9.0.custom.min.js"></script>
    <script type="text/javascript" src="/static/js/libs/smoothie.js"></script>
    <script type="text/javascript" src="/static/js/libs/moment.min.js"></script>
    <script src="/static/js/libs/less-1.3.1.min.js" type="text/javascript"></script>
 </head>

 <body>
 
 <div id="chamberdiv">
 <img id="chamber" src="/static/img/chamber.png" alt="Vacuum chamber" width="1361" height="300">
 </div>

%for i in range(len(sensors)):
   <div id="{{ sensors[i]['dbid'] }}div" class="showvals {{ 'pressurediv' if sensors[i]['type'] == 'pressure' else ''}}">
    <label class="fieldlabel">{{ sensors[i]['name'] }}</label>
    <input id="{{ sensors[i]['dbid']}}val" value="??.??" size="13">
   </div>
%end

<!-- Charts -->
%for i in range(len(sensors)):
   <div id="{{ sensors[i]['dbid'] }}cdiv" class="charts">
    <label class="fieldlabel">{{ sensors[i]['name'] }}</label>
    <canvas id="{{ sensors[i]['dbid'] }}chart" class="tcchart" width="550" height="170"></canvas>
   </div>
%end

 <div id="messages">
  <textarea id="messagebox"></textarea>
 </div>

 <div id="spanselect">
   <input type="radio" id="timespan1" name="radio" checked="checked" /><label for="timespan1">10 min</label>
   <input type="radio" id="timespan2" name="radio" /><label for="timespan2">1h</label>
   <input type="radio" id="timespan3" name="radio" /><label for="timespan3">12h</label>
   <input type="radio" id="timespan4" name="radio" /><label for="timespan4">24h</label>
 </div>

 <div id="loading">
  Loading data, please wait...
 </div>

 <div id="time">
 </div>

 <div id="timestamp">
 </div>

 <div id="links">
  <a href="/export" target="_blank">Export data</a><br>
  <!-- <a href="/rga" target="_blank">RGA</a> -->
 </div>

<!-- Final Scripts -->
<script src="/static/js/libs/less-1.3.1.min.js" type="text/javascript"></script>
<!-- This part is duing the heavy duty -->
<script type="text/javascript">
// Bakeout related script

var lastsince;

var fields;
var msg;
var loadmsg;

var readyformore = false;
var lasttime;

// Time updating on the screen
var timer = document.getElementById("time");
var updateTime = function() {
    timer.innerHTML = moment().format('H:mm:ss');
};
updateTime();
var timedisplay = setInterval(updateTime, 1000);

var chw = 550;
var spans = [10 * 60 * 1000 / chw, 60 * 60 * 1000 / chw, 12 * 60 * 60 * 1000 / chw, 24 * 60 * 60 * 1000 / chw];  // 10 mins, 1 hour, 12 hours, 24 hours
var grids = [60 * 1000, 5 * 60 * 1000, 60 * 60 * 1000, 60 * 60 * 1000]; // 1 min, 5 mins, 1 hour
var limits = {
%for i in range(len(sensors)):
  "{{ sensors[i]['dbid'] }}" : {{ sensors[i]['warning'] }} {{ ','  if (i < len(sensors)-1) else '' }}
%end
  };

var stalethreshold = 15 * 1000;  // milliseconds, if no reading for more than this time, show it as stale

var markstale = function(id) {
  $("#"+id+"val").addClass("stale");
}

var stalectr = {};

var showReadings = function(data, first) {
    if (data.result != 'OK') {
        message(data.result);
    } else {
        if (first) {
            var num = series.length-1;
            do {
		series[num].data = [];
            } while( num-- );
        };
        readings = data.readings;
        var readnum = readings.length - 1;
        var now = new Date().getTime();
        for (var readnum = 0; readnum < readings.length; readnum++) {
            reading = readings[readnum];
            if (!reading) {
                continue;
            }
            if (fields[reading['id']]) {
                var rid = reading['id']
		if (limits[rid] && (limits[rid] <= reading.reading.value)) {
                    $("#"+rid+"val").addClass("warning");
		} else {
                    $("#"+rid+"val").removeClass("warning");
		};  // End of if-warning

                var timestamp = new Date(reading.date).getTime();
		if (reading.type == 'temperature') {
		    if (reading.reading.value < 1000) {
			thisone = fields[rid];
			thisone['value'].val(reading.reading.value+' '+reading.reading.unit);
			thisone['chart'].append(timestamp, reading.reading.value);
		    } else {
			message(moment(reading.date).format()+" Error on channel "+rid+": "+reading.err);
		    };
		} else if (reading.type == 'pressure') {
                    thisone = fields[rid];
                    thisone['value'].val(reading.reading.value.toExponential()+' '+reading.reading.unit);
                    var logval = Math.log(reading.reading.value) / Math.LN10;
                    thisone['chart'].append(timestamp, logval);
		}; // end of if-type
                lasttime = moment(reading.date).format('MMMM Do YYYY, H:mm:ss.SSS');

                if ((now - timestamp) > stalethreshold) {
                   $("#"+rid+"val").addClass("stale");
                } else {
                   $("#"+rid+"val").removeClass("stale");
                }
                if (stalectr[rid]) {
                   clearTimeout(stalectr[rid]);
                }
                stalectr[rid] = setTimeout(markstale, stalethreshold, rid); // apparently works on Chrome while closure form gets wrong parameters
            } else {
		<!-- console.log("Missing id:"+reading['id']); -->
            }; // end of if-id-known
        }; // end of readings loop
        $("#timestamp").html(lasttime);
        for (var i=0; i < series.length; i++) {
           series[i].data.sort(function(a, b) {return a[0]-b[0];});
        }
    }; // end of data.result OK
}; // end of showReadings

   var getdate = function () {
      return moment().format('MMMM Do YYYY, h:mm:ss.SSS a');
   }
   var message = function(todisplay) {
      msg.text(todisplay+'\n'+msg.text());
   }

   var reread = function() {
      if (readyformore) {
          getdata(lastsince, moment(), showReadings, false);
      };
   }

var getdata = function(since, till, cb, first) {
     readyformore = false;
     loadmsg.removeClass("hidden");
     if (first) {
         lasttime = '';
         $("#timestamp").html(lasttime);
		 }
     var request = $.ajax({url: '/readings',
			   data: {'sincedate': since.format("YYYY-MM-DDTHH:mm:ss.SSSZ"),  // Include milliseconds!
				  'tilldate':  till.format("YYYY-MM-DDTHH:mm:ss.SSSZ"),
                                  'limit': 10000,
				 }
			  });

     request.done(function(data) {
	 if (data.result == 'OK') {
             if (data.readings.length == 0) {
                lastsince = till;
                readyformore = true;
                loadmsg.addClass("hidden");
             } else {
                cb(data, first);
                var lasttime = moment(data.readings[data.readings.length-1].date);
                getdata(lasttime, till, cb, false);
             }
	 } else {
           message(data.result);
           readyformore = true;
           loadmsg.addClass("hidden");
         }
     });

     request.fail(function(jqXHR, textStatus) {
      console.log( "Request failed: " + textStatus );
      readyformore = true;
      loadmsg.addClass("hidden");
     });
   }

var charts = [
%for i in range(len(sensors)):
  new SmoothieChart({'interpolation': 'line' {{! ", 'scale' : 'log'" if (sensors[i]['type'] == 'pressure') else '' }} }) {{ ','  if (i < len(sensors)-1) else '' }}
%end
];

var series = [
%for i in range(len(sensors)):
  new TimeSeries() {{ ','  if (i < len(sensors)-1) else '' }}
%end
];

   $(document).ready(function() {
     var rereadID;
     $( "#spanselect" ).buttonset();
     msg = $("#messagebox");
     loadmsg = $("#loading");

     fields = {
%for i in range(len(sensors)):
  "{{ sensors[i]['dbid'] }}": {"value": $("#{{ sensors[i]['dbid'] }}val"), "chart": series[{{ i }}]} {{ ','  if (i < len(sensors)-1) else '' }}
%end
};

%for i in range(len(sensors)):
      chart = charts[{{ i }}];
      chart.addTimeSeries(series[{{ i }}], { strokeStyle:'rgb({{ '150, 150, 255' if (sensors[i]['type'] == 'pressure') else '255, 255, 255'}})', lineWidth:2 });
      chart.options.millisPerPixel = spans[0];
      chart.options.grid.millisPerLine = grids[0];
      chart.streamTo(document.getElementById("{{ sensors[i]['dbid'] }}chart"));
%end

      var since = moment().subtract('minutes', 10);
      getdata(since, moment(), showReadings, true);
      rereadID = setInterval(reread, 2000);

      var selectSpan = function(span) {
        clearInterval(rereadID);
        for(var i = 0; i < {{ len(sensors) }}; i++) {
          chart = charts[i];
          series[i].data=[];
          chart.options.millisPerPixel = spans[span];
          chart.options.grid.millisPerLine = grids[span];
        }
        var minutes = spans[span]*chw/(1000*60);
        var since = moment().subtract('minutes', minutes);
        getdata(since, moment(), showReadings, true);
        rereadID = setInterval(reread, 2000);
      };

      $("#timespan1").click(function() {
			 selectSpan(0);
			 });
      $("#timespan2").click(function() {
			 selectSpan(1);
			 });
      $("#timespan3").click(function() {
			 selectSpan(2);
			 });
      $("#timespan4").click(function() {
			 selectSpan(3);
			 });
   });
</script>


 </body>
</html>
