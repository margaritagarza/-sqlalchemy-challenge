import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return precipitation info"""
    # Query precipitations
    #query for dates and find latest
    latestDate = (session.query(Measurement.date)
                        .order_by(Measurement.date.desc())
                        .first())

    #extract string from query object
    latestDate = list(np.ravel(latestDate))[0]
    #convert date string to datetime object
    latestDate = dt.datetime.strptime(latestDate, '%Y-%m-%d')

    #extract year, month, and day as integers
    latestYear = int(dt.datetime.strftime(latestDate, '%Y'))
    latestMonth = int(dt.datetime.strftime(latestDate, '%m'))
    latestDay = int(dt.datetime.strftime(latestDate, '%d'))

    #calculate one year before latest date
    yearBefore = dt.date(latestYear, latestMonth, latestDay) - dt.timedelta(days=365)

    #query for dates and precipitation for the latest year
    rainData = (session.query(Measurement.date, Measurement.prcp)
                    .filter(Measurement.date > yearBefore)
                    .order_by(Measurement.date)
                    .all())
    # rainData ==> [(date1, prcp1),(date2,prcp2)....]
    session.close()

    # Convert list of tuples into normal list
    rain_list = {date:prcp for date, prcp in rainData}

    return jsonify(rain_list)

@app.route("/api/v1.0/stations")
def stations():
     # Create our session (link) from Python to the DB
    session = Session(engine)


    # Design a query to show how many stations are available in this dataset?
    station_query = session.query(Station.id, Station.name)

    # Convert list of tuples into normal list
    station_list = {id:name for id, name in station_query}
    print(station_list)
    
    session.close()

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query precipitations
    #query for dates and find latest
    latestDate = (session.query(Measurement.date)
                        .order_by(Measurement.date.desc())
                        .first())

    #extract string from query object
    latestDate = list(np.ravel(latestDate))[0]
    #convert date string to datetime object
    latestDate = dt.datetime.strptime(latestDate, '%Y-%m-%d')

    #extract year, month, and day as integers
    latestYear = int(dt.datetime.strftime(latestDate, '%Y'))
    latestMonth = int(dt.datetime.strftime(latestDate, '%m'))
    latestDay = int(dt.datetime.strftime(latestDate, '%d'))

    #calculate one year before latest date
    yearBefore = dt.date(latestYear, latestMonth, latestDay) - dt.timedelta(days=365)


    # What are the most active stations? (i.e. what stations have the most rows)?
    # List the stations and the counts in descending order.
    stationCounts = (session.query(Measurement.station, func.count(Measurement.station))
                        .group_by(Measurement.station)
                        .order_by(func.count(Measurement.station).desc())
                        .all())
    stationCounts

    #set the most active station
    stationID = stationCounts[0][0]


    #query for the last year of temperature data
    tempData = (session.query(Measurement.date, Measurement.tobs)
                   .filter(Measurement.date > yearBefore)
                   .filter(Measurement.station == stationID)
                   .order_by(Measurement.date)
                   .all())
    #tempTable.reset_index(inplace=True)
    
    # Convert list of tuples into normal list
    temp_list = {date:tobs for date, tobs in tempData}
    #temp_list=pd.Series(tempTable.tobs.values, index=tempTable.date).to_dict()
    #temp_list = {tobs:tobs for date, tobs in tempTable}
    #print(jsonify(temp_list))
    #temp_list1 = [x for x in tempTable['date']]
    #temp_list2 = [x for x in tempTable[]]
    session.close()

    return jsonify(temp_list)
  
@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)


    # Design a query to show how many stations are available in this dataset?
    date_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    print(date_query)

    session.close()
    # function usage example
    return  
    jsonify(date_query)

if __name__ == '__main__':
    app.run(debug=True)
