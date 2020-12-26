// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

function number_format(number, decimals, dec_point, thousands_sep) {
  // *     example: number_format(1234.56, 2, ',', ' ');
  // *     return: '1 234,56'
  number = (number + '').replace(',', '').replace(' ', '');
  var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function(n, prec) {
      var k = Math.pow(10, prec);
      return '' + Math.round(n * k) / k;
    };
  // Fix for IE parseFloat(0.55).toFixed(0) = 0;
  s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
  if (s[0].length > 3) {
    s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
  }
  if ((s[1] || '').length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1).join('0');
  }
  return s.join(dec);
}


function selectFunction()
{
	var option_value = document.getElementById('project_id').value;
	renderProject(option_value);
}

$(document).ready(function(){   
	renderProject(0);

});


function renderProject(option_value)
{
	$.ajax({
	

		url:'/manager-dashboard/project/' + option_value,
		type:'GET',
		dataType:'json',
success:(data) => {  


	var data_points = 	[]
	var color_buffer = 100 / data.project_list.length



	for(i in data.project_list)
		{
			var r_quotient = 62 + color_buffer;
			var g_quotient = 28 + color_buffer;
			var b_quotient = 118 + color_buffer;
			var light_color_scheme = "rgba("+r_quotient+" , "+g_quotient+" , "+b_quotient+" , 0.05)"
			var heavy_color_scheme = "rgba("+r_quotient+" , "+g_quotient+" , "+b_quotient+" , 1)"
			var project_data_points = []
			var label_points = []
			for(j=0; j< data.chart_data.length; j++)
			{	
				if(data.chart_data[j].p_id == data.project_list[i].id)
				{
					project_data_points.push(data.chart_data[j].cnt);
					label_points.push(data.chart_data[j].mth_name)
				}
				
			}
			data_points.push({

			  label: data.project_list[i].name,
			  lineTension: 0.3,
			  backgroundColor: light_color_scheme,
			  borderColor: heavy_color_scheme,
			  pointRadius: 3,
			  pointBackgroundColor: heavy_color_scheme,
			  pointBorderColor: heavy_color_scheme,
			  pointHoverRadius: 3,
			  pointHoverBackgroundColor: heavy_color_scheme,
			  pointHoverBorderColor: heavy_color_scheme,
			  pointHitRadius: 10,
			  pointBorderWidth: 2,
			  data: project_data_points,
				
			})

			color_buffer = color_buffer + color_buffer
			
				}
			
	// Area Chart Example
	$('#myAreaChart').remove();
      $('#line-chart').append('<canvas id="myAreaChart"><canvas>');

	var ctx = document.getElementById("myAreaChart");
	var myLineChart = new Chart(ctx, {
	  type: 'line',
	  data: {
		labels: label_points,
		datasets:  data_points
		
		,
	  },

	  options: {
		maintainAspectRatio: false,
		layout: {
		  padding: {
			left: 10,
			right: 25,
			top: 25,
			bottom: 0
		  }
		},
		scales: {
		  xAxes: [{
			time: {
			  unit: 'date'
			},
			scaleLabel: {
				display: true,
				labelString: 'Month'
			  },
			gridLines: {
			  display: false,
			  drawBorder: false
			},
			ticks: {
			  maxTicksLimit: 12
			}
		  }],
		  yAxes: [{
			scaleLabel: {
				display: true,
				labelString: 'Tickets'
			  },
			ticks: {
			  stepSize:5,
			  maxTicksLimit: 5,
			  padding: 10,
			  // Include a dollar sign in the ticks
			  callback: function(value, index, values) {
				return number_format(value);
			  }
			},
			gridLines: {
			  color: "rgb(234, 236, 244)",
			  zeroLineColor: "rgb(234, 236, 244)",
			  drawBorder: false,
			  borderDash: [2],
			  zeroLineBorderDash: [2]
			}
		  }],
		},
		legend: {
		  display: true,
		  position: "bottom"
		},
		tooltips: {
		  backgroundColor: "rgb(255,255,255)",
		  bodyFontColor: "#858796",
		  titleMarginBottom: 10,
		  titleFontColor: '#6e707e',
		  titleFontSize: 14,
		  borderColor: '#dddfeb',
		  borderWidth: 1,
		  xPadding: 15,
		  yPadding: 15,
		  displayColors: false,
		  intersect: false,
		  mode: 'index',
		  caretPadding: 10,
		  callbacks: {
			label: function(tooltipItem, chart) {
			  var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
			  return datasetLabel + ':' + number_format(tooltipItem.yLabel);
			}
		  }
		}
	  }
	});

}});
}