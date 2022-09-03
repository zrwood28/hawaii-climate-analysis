import numpy as np
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect = True)

Station = Base.classes.station
Measurement = Base.classes.measurement

app = Flask(__name__)

@app.route("/")
def home():

    "List navigation routes around the site."

    return(
        f"Welcome to the Hawaii Climate Page!<br/>"
        f"-------------------------------------<br/>"
        f"Available navigation routes for this site:<br/>"
        f"<br/>"
        f"/api/v1.0/precipatation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"-------------------------------------<br/>"
        f"The following routes are customizable: <br/>"
        f"<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
        f"<br/>"
        f"Range of possible dates: 2010-01-01 through 2017-08-23."
    )


@app.route("/api/v1.0/precipatation")
def precipatation():

    "Dictionary of dates between 8/23/16 and 8/23/17 and their precipatation levels."

    session = Session(engine)

    last_date = dt.date(2017, 8, 23)
    first_date = last_date - dt.timedelta(days = 365)

    prcp_date = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= first_date, Measurement.date <= last_date)\
        .order_by(Measurement.date).all()

    session.close()

    prcp_by_day = []

    for date, prcp in prcp_date:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_by_day.append(prcp_dict)

    return jsonify(prcp_by_day)


@app.route("/api/v1.0/stations")
def stations():

    "List of all stations that recorded climate data."

    session = Session(engine)

    stations = session.query(Station.name).all()

    session.close()

    stations_list = list(np.ravel(stations))

    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():

    "List the observed temperatures from Waihee Station over the last year of recording."

    session = Session(engine)

    last_date = dt.date(2017, 8, 23)
    first_date = last_date - dt.timedelta(days = 365)

    waihee_lastyr = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == 'USC00519281', Measurement.date >= first_date,\
        Measurement.date <= last_date).all()

    session.close()

    waihee_list = list(np.ravel(waihee_lastyr))

    return jsonify(waihee_list)


@app.route("/api/v1.0/<start>")
def start_date(start):

    "List the minimum, average, and maximum temperature for a specified range using a start date."

    session = Session(engine)

    descriptives = [func.min(Measurement.tobs).label("min"), func.avg(Measurement.tobs).label("avg"),\
        func.max(Measurement.tobs).label("max")]

    temp_stats = session.query(* descriptives).filter(Measurement.date >= start).all()

    session.close()

    temps_stats_list = []
    for min, avg, max in temp_stats:
        temps_dict = {}
        temps_dict["min temp"] = min
        temps_dict["avg temp"] = round(avg, 2)
        temps_dict["max temp"] = max
        temps_stats_list.append(temps_dict)

    return jsonify(temps_stats_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):

    "List descriptives for a specified range using both a start date and an end date."

    session = Session(engine)

    descriptives_se = [func.min(Measurement.tobs).label("min"), func.avg(Measurement.tobs).label("avg"),\
        func.max(Measurement.tobs).label("max")]

    temp_stats_se = session.query(* descriptives_se).filter\
        (Measurement.date >= start, Measurement.date <= end).all()

    session.close()

    temp_stats_list_se = []
    for min, avg, max in temp_stats_se:
        temps_dict_se = {}
        temps_dict_se["min temp"] = min
        temps_dict_se["avg temp"] = round(avg, 2)
        temps_dict_se["max temp"] = max
        temp_stats_list_se.append(temps_dict_se)

    return jsonify(temp_stats_list_se)

if __name__ == "__main__":
    app.run(debug = True)