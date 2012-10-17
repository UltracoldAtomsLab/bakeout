// Bakeout related script

var lastsince;

var fields;
var msg;
var loadmsg;

var readyformore = false;

// Time updating on the screen
var timer = document.getElementById("time");
var updateTime = function() {
    timer.innerHTML = moment().format('H:mm:ss');
};
updateTime();
var timedisplay = setInterval(updateTime, 1000);

var chw = 550;
var spans = [10 * 60 * 1000 / chw, 60 * 60 * 1000 / chw, 12 * 60 * 60 * 1000 / chw];  // 10 mins, 1 hour, 12 hours
var grids = [60 * 1000, 5 * 60 * 1000, 60 * 60 * 1000]; // 1 min, 5 mins, 1 hour
var limits = {"tc0": 202,
              "tc1": 202,
              "tc3": 162,
              "tc8": 162,
              "tc11": 162,
              "tc14": 192
             };

   var showReadings = function(data) {
       if (data.result != 'OK') {
         message(data.result);
       } else {
         readings = data.readings;
         for (var i = 0; i < readings.length; i++) {
           reading = readings[i];
           if (fields[reading['id']]) {
            if (reading.type == 'temperature') {
              if (reading.reading.value < 1000) {
                if (limits[reading['id']] && (limits[reading['id']] <= reading.reading.value)) {
                   $("#"+reading['id']+"val").addClass("warning");
                } else {
                   $("#"+reading['id']+"val").removeClass("warning");
                }
                thisone = fields[reading['id']];
                thisone['value'].val(reading.reading.value+' '+reading.reading.unit);
                thisone['chart'].append(new Date(reading.date).getTime(), reading.reading.value);
              } else {
                message(moment(reading.date).format()+" Error on channel "+reading['id']+": "+reading.err);
              }
            } else if (reading.type == 'pressure') {
                thisone = fields[reading['id']];
                thisone['value'].val(reading.reading.value.toExponential()+' '+reading.reading.unit);
                var logval = Math.log(reading.reading.value) / Math.LN10;
                thisone['chart'].append(new Date(reading.date).getTime(), logval);
            }
           } else {
             console.log("Missing id:"+reading['id']);
           }
        }
      }
      readyformore = true;
      loadmsg.addClass("hidden");
   }

   var getdate = function () {
      return moment().format('MMMM Do YYYY, h:mm:ss a');
   }
   var message = function(todisplay) {
      msg.text(todisplay+'\n'+msg.text());
   }

   var reread = function() {
      if (readyformore) {
        lastsince = getdata(lastsince, showReadings);
      };
   }

   var getdata = function(since, cb) {
     readyformore = false;
     loadmsg.removeClass("hidden");
     var now = moment();
     $.ajax({url: '/readings',
             data: {'sincedate': now.toDate(),
                    'tilldate':  since.toDate()
                    },
             success: function(data) { cb(data) }
            });
     return now;
   }

   var charts = [new SmoothieChart(),
                 new SmoothieChart(),
                 new SmoothieChart(),
                 new SmoothieChart(),
                 new SmoothieChart(),
                 new SmoothieChart(),
                 new SmoothieChart(),
                 new SmoothieChart(),
                 new SmoothieChart(),
                 new SmoothieChart(),
                 new SmoothieChart(),
                 new SmoothieChart(),
                 new SmoothieChart(),
                 new SmoothieChart(),
                 new SmoothieChart(),
                 new SmoothieChart(),
                 new SmoothieChart(),
                 new SmoothieChart()
                ];
   var series = [new TimeSeries(),
                 new TimeSeries(),
                 new TimeSeries(),
                 new TimeSeries(),
                 new TimeSeries(),
                 new TimeSeries(),
                 new TimeSeries(),
                 new TimeSeries(),
                 new TimeSeries(),
                 new TimeSeries(),
                 new TimeSeries(),
                 new TimeSeries(),
                 new TimeSeries(),
                 new TimeSeries(),
                 new TimeSeries(),
                 new TimeSeries(),
                 new TimeSeries(),
                 new TimeSeries()
                 ];

   $(document).ready(function() {
     var rereadID;
     $( "#spanselect" ).buttonset();
     msg = $("#messagebox");
     loadmsg = $("#loading");

     fields = {"tc0": {"value": $("#tc0val"), "chart": series[0]},
               "tc1": {"value": $("#tc1val"), "chart": series[1]},
               "tc2": {"value": $("#tc2val"), "chart": series[2]},
               "tc3": {"value": $("#tc3val"), "chart": series[3]},
               "tc4": {"value": $("#tc4val"), "chart": series[4]},
               "tc5": {"value": $("#tc5val"), "chart": series[5]},
               "tc6": {"value": $("#tc6val"), "chart": series[6]},
               "tc7": {"value": $("#tc7val"), "chart": series[7]},
               "tc8": {"value": $("#tc8val"), "chart": series[8]},
               "tc9": {"value": $("#tc9val"), "chart": series[9]},
               "tc10": {"value": $("#tc10val"), "chart": series[10]},
               "tc11": {"value": $("#tc11val"), "chart": series[11]},
               "tc12": {"value": $("#tc12val"), "chart": series[12]},
               "tc13": {"value": $("#tc13val"), "chart": series[13]},
               "tc14": {"value": $("#tc14val"), "chart": series[14]},
               "tc15": {"value": $("#tc15val"), "chart": series[15]},
               "coldpoint": {"value": $("#coldval"), "chart": series[16]},
               "vc0": {"value": $("#gauge1val"), "chart": series[17]}
      };

      var since = moment().subtract('minutes', 10);
      lastsince = getdata(since, showReadings);

      rereadID = setInterval(reread, 2000);
      for(var i = 0; i < 16; i++) {
         chart = charts[i];
         chart.addTimeSeries(series[i], { strokeStyle:'rgb(255, 255, 255)', lineWidth:2 });
         chart.options.millisPerPixel = spans[0];
         chart.options.grid.millisPerLine = grids[0];
         chart.streamTo(document.getElementById("tc"+i+"chart"));
         chart.fps = 1;
      }
         chart = charts[16];
         chart.addTimeSeries(series[16], { strokeStyle:'rgb(255, 255, 255)', lineWidth:2 });
         chart.options.millisPerPixel = spans[0];
         chart.options.grid.millisPerLine = grids[0];
         chart.streamTo(document.getElementById("coldchart"));
         chart.fps = 1;

         chart = charts[17];
         chart.addTimeSeries(series[17], { strokeStyle:'rgb(150, 150, 255)', lineWidth:2 });
         chart.options.millisPerPixel = spans[0];
         chart.options.grid.millisPerLine = grids[0];
         chart.streamTo(document.getElementById("gauge1chart"));
         chart.fps = 1;

      var selectSpan = function(span) {
        clearInterval(rereadID);
        for(var i = 0; i < 16; i++) {
          chart = charts[i];
          series[i].data=[];
          chart.options.millisPerPixel = spans[span];
          chart.options.grid.millisPerLine = grids[span];
        }
        chart = charts[16];
        series[16].data=[];
        chart.options.millisPerPixel = spans[span];
        chart.options.grid.millisPerLine = grids[span];

        chart = charts[17];
        series[17].data=[];
        chart.options.millisPerPixel = spans[span];
        chart.options.grid.millisPerLine = grids[span];

        var minutes = spans[span]*chw/(1000*60);
        var since = moment().subtract('minutes', minutes);
        lastsince = getdata(since, showReadings);
        rereadID = setInterval(reread, 2000);
      };

      $("#radio1").click(function() {
			 selectSpan(0);
			 });
      $("#radio2").click(function() {
			 selectSpan(1);
			 });
      $("#radio3").click(function() {
			 selectSpan(2);
			 });
   });
