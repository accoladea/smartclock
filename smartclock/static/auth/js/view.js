        $.getJSON((window.origin + "/api/v1/timesheets/" + ($("#username").text()).trim()), function (response) {
            var timesheets = response;
            console.log(JSON.stringify(timesheets));
            if (timesheets.length == 0){
                $("#timesheets_table").append('<h5>The timesheets are empty!</h5>');
            } else {

                var headerRow = "";
                var bodyRows = "";

                function format_it(time) {
                    return (moment(time).local().format('LTS')).toString();
                }

                function bring_it(date) {
                    return (moment(date).local().format('L dddd')).toString();
                }

                function get_them(start, end) {
//                     var a = moment(start);
//                     var b = moment(end);
//                     var result = b.diff(a, true);
//                     return moment(result).format('LTS').toString();
                    return getStamp(start, end);
                }

                headerRow += '<th scope="col">Time In:</th>\n';
                headerRow += '<th scope="col">Time Out:</th>\n';
                headerRow += '<th scope="col">Worked HRs:</th>\n';

                if (!($.isEmptyObject(timesheets))) {
                   for (let ts of timesheets) {

                        if (bodyRows.includes(bring_it(ts.date))===false) {
                            // this if checks if the date is not already in bodyRows
                            bodyRows += '<tr>\n';
                            bodyRows += '<th class="bg-light py-1 text-dark text-center" scope="row" colspan="3">'+bring_it(ts.date)+'</th>\n';
                            bodyRows += '</tr>\n';
                        }
                        bodyRows += '<tr>\n';
                        bodyRows += '<td>' + format_it(ts.clock_in_time) + '</td>\n';
                        bodyRows += '<td>' + format_it(ts.clock_out_time) + '</td>\n';
                        bodyRows += '<td>' + get_them(ts.clock_in_time, ts.clock_out_time) + '</td>\n';
                        bodyRows += '</tr>\n';
                    }
                }

                 $("#timesheets_table").append('<table class="table table-bordered  table-dark table-sm table-hover table-striped">\n'+
                '<thead>\n<tr>' + headerRow +'</tr>\n</thead>\n'+
                '<tbody>\n' + bodyRows + '</tbody>\n</table>');

            }
        });


        function getStamp(start, end) {
            function paddy(num) {
                // adds leading zeros
                var pad_char = '0';
                var padlen = 2;
                var pad = new Array(1 + padlen).join(pad_char);
                return (pad + num).slice(-pad.length);
            }

            // start time and end time
            var t = "";

            var start = moment(start);
            var end = moment(end);

            // calculate total duration
            var duration = moment.duration(end.diff(start));

            // duration in hours
            var hours = parseInt(duration.asHours());

            if (hours !== 0) {
                t = t + String(paddy(hours)) + ':';
            } else {
                t = t + '00' + ':';
            }

            // duration in minutes
            var minutes = parseInt(duration.asMinutes())%60;
            if (minutes !== 0) {
                t = t + String(paddy(minutes)) + ':';
            } else {
                t = t + '00' + ':';
            }

            // duration in seconds
            var seconds = parseInt(duration.asSeconds())%60;
            if (seconds !== 0) {
                t = t + String(paddy(seconds));
            } else {
                t = t + '00';
            }
            return t
        }




