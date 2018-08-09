#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sidereal.py: A Python module for astronomical calculations.

  For documentation, see:
    ims/
"""
MODULE = "sidereal.py: A Python spherical trigonometry package"
VERSION = "1.0"

# - - - - -   I m p o r t s
import math
import re
import datetime
#================================================================
# Manifest constants
#----------------------------------------------------------------

FIRST_GREGORIAN_YEAR = 1583
TWO_PI = 2.0 * math.pi
PI_OVER_12 = math.pi / 12.0
JULIAN_BIAS = 2400000    # 2,400,000
DMS_UNITS = (60, 60)
SIDEREAL_A = 0.0657098
FLOAT_PAT = re.compile (
    r'\d+'          # Matches one or more digits
    r'('            # Start optional fraction
      r'[.]'          # Matches the decimal point
      r'\d+'          # Matches one or more digits
    r')?')          # End optional group
D_PAT = re.compile(r'[dD]')
M_PAT = re.compile(r'[mM]')
S_PAT = re.compile(r'[sS]')
H_PAT = re.compile(r'[hH]')
NS_PAT = re.compile(r'[nNsS]')
EW_PAT = re.compile(r'[eEwW]')

# - - -   h o u r s T o R a d i a n s

def hoursToRadians(hours):
    """Convert hours (15 degrees) to radians.
    """
    return  hours * PI_OVER_12

# - - -   r a d i a n s T o H o u r s

def radiansToHours(radians):
    """Convert radians to hours (15 degrees).
    """
    return  radians / PI_OVER_12

# - - -   h o u r A n g l e T o R A

def hourAngleToRA(h, ut, eLong):
    """Convert hour angle to right ascension.

      [ (h is an hour angle in radians as a float) and
        (ut is a timestamp as a datetime.datetime instance) and
        (eLong is an east longitude in radians) ->
          return the right ascension in radians corresponding
          to that hour angle at that time and location ]
    """
    #-- 1 --
    # [ gst  :=  the Greenwich Sidereal Time equivalent to
    #            ut, as a SiderealTime instance ]
    gst = SiderealTime.fromDatetime(ut)
    #-- 2 --
    # [ lst  :=  the local time corresponding to gst at
    #            longitude eLong ]
    lst = gst.lst(eLong)
    #-- 3 --
    # [ alpha  :=  lst - h, normalized to [0,2*pi) ]
    alpha = (lst.radians - h) % TWO_PI

    #-- 4 --
    return alpha

# - - -   r a T o H o u r A n g l e

def raToHourAngle(ra, ut, eLong):
    """Convert right ascension to hour angle.

      [ (ra is a right ascension in radians as a float) and
        (ut is a timestamp as a datetime.datetime instance) and
        (eLong is an east longitude in radians) ->
          return the hour angle in radians at that time and
          location corresponding to that right ascension ]
    """
    #-- 1 --
    # [ gst  :=  the Greenwich Sidereal Time equivalent to
    #            ut, as a SiderealTime instance ]
    gst = SiderealTime.fromDatetime(ut)

    #-- 2 --
    # [ lst  :=  the local time corresponding to gst at
    #            longitude eLong ]
    lst = gst.lst(eLong)
    #-- 3 --
    # [ h  :=  lst - ra, normalized to [0,2*pi) ]
    h = (lst.radians - ra) % TWO_PI

    #-- 4 --
    return h

# - - -   d a y N o

def dayNo(dt):
    """Compute the day number within the year.

      [ dt is a date as a datetime.datetime or datetime.date ->
          return the number of days between dt and Dec. 31 of
          the preceding year ]
    """
    #-- 1 --
    # [ dateOrd  :=  proleptic Gregorian ordinal of dt
    #   jan1Ord  :=  proleptic Gregorian ordinal of January 1
    #                of year (dt.year) ]
    dateOrd = dt.toordinal()
    jan1Ord = datetime.date(dt.year, 1, 1).toordinal()

    #-- 2 --
    return dateOrd - jan1Ord + 1

# - - -   p a r s e D a t e t i m e

T_PATTERN = re.compile('[tT]')

def parseDatetime(s):
    """Parse a date with optional time.

      [ s is a string ->
          if s is a valid date with optional time ->
            return that timestamp as a datetime.datetime instance
          else -> raise SyntaxError ]
    """
    #-- 1 --
    # [ if s contains "T" or "t" ->
    #     rawDate  :=  s up to the first such character
    #     rawTime  :=  s from just after the first such
    #                  character to the end
    #   else ->
    #     rawDate  :=  s
    #     rawTime  :=  None ]
    m = T_PATTERN.search(s)
    if  m is None:
        rawDate, rawTime = s, None
    else:
        rawDate = s[:m.start()]
        rawTime = s[m.end():]
    #-- 2 --
    # [ if rawDate is a valid date ->
    #     datePart  :=  rawDate as a datetime.datetime instance
    #   else -> raise SyntaxError ]
    datePart = parseDate(rawDate)
    #-- 3 --
    # [ if rawTime is None ->
    #     timePart  :=  00:00 as a datetime.time
    #   else if rawTime is valid ->
    #     timePart  :=  rawTime as a datetime.time
    #   else -> raise SyntaxError ]
    if  rawTime is None:
        timePart = datetime.time(0, 0)
    else:
        timePart = parseTime(rawTime)
    #-- 4 --
    return datetime.datetime.combine(datePart, timePart)

# - - -   p a r s e D a t e

YEAR_FIELD = "Y"
MONTH_FIELD = "M"
DAY_FIELD = "D"

dateRe = (
    r'('            # Begin YEAR_FIELD
      r'?P<%s>'       # Name this group YEAR_FIELD
      r'\d{4}'        # Match exactly four digits
    r')'            # End YEAR_FIELD
    r'\-'           # Matches one hyphen
    r'('            # Begin MONTH_FIELD
      r'?P<%s>'       # Name this group MONTH_FIELD
      r'\d{1,2}'      # Matches one or two digits
    r')'            # End MONTH_FIELD
    r'\-'           # Matches "-"
    r'('            # Begin DAY_FIELD
      r'?P<%s>'       # Name this group DAY_FIELD
      r'\d{1,2}'      # Matches one or two digits
    r')'            # End DAY_FIELD
    r'$'            # Make sure all characters match
   ) % (YEAR_FIELD, MONTH_FIELD, DAY_FIELD)
DATE_PAT = re.compile(dateRe)

def parseDate(s):
    """Validate and convert a date in external form.

      [ s is a string ->
          if s is a valid external date string ->
            return that date as a datetime.date instance
          else -> raise SyntaxError ]
    """
    #-- 1 --
    # [ if DATE_PAT matches s ->
    #     m  :=  a match instance describing the match
    #   else -> raise SyntaxError ]
    m = DATE_PAT.match(s)
    if  m is None:
        raise SyntaxError("Date does not have pattern YYYY-DD-MM: "
                          "'{0}'".format(s))
    #-- 2 --
    year  = int(m.group(YEAR_FIELD))
    month = int(m.group(MONTH_FIELD))
    day   = int(m.group(DAY_FIELD))

    #-- 3 --
    return datetime.date(year, month, day)

# - - -   p a r s e T i m e

def parseTime(s):
    """Validate and convert a time and optional zone.

      [ s is a string ->
          if s is a valid time with optional zone suffix ->
            return that time as a datetime.time
          else -> raise SyntaxError ]
    """
    #-- 1 -
    # [ if s starts with FLOAT_PAT ->
    #     decHour  :=  matching part of s as a float
    #     minuteTail  :=  part s past the match
    #   else -> raise SyntaxError ]
    decHour, minuteTail = parseFloat(s, "Hour number")
    #-- 2 --
    # [ if minuteTail starts with ":" followed by FLOAT_PAT ->
    #     decMinute  :=  part matching FLOAT_PAT as a float
    #     secondTail  :=  part of minuteTail after the match
    #   else if minuteTail starts with ":" not followed by
    #   FLOAT_PAT ->
    #     raise SyntaxError
    #   else ->
    #     decMinute  :=  0.0
    #     secondTail  :=  minuteTail ]
    if  minuteTail.startswith(':'):
        m = FLOAT_PAT.match(minuteTail[1:])
        if  m is None:
            raise SyntaxError("Expecting minutes: '{0}'".format(
                              minuteTail))
        else:
            decMinute = float(m.group())
            secondTail = minuteTail[m.end()+1:]
    else:
        decMinute = 0.0
        secondTail = minuteTail
    #-- 3 --
    # [ if secondTail starts with ":" followed by FLOAT_PAT ->
    #     decSecond  :=  part matching FLOAT_PAT as a float
    #     zoneTail  :=  part of secondTail after the match
    #   else if secondTail starts with ":" not followed by
    #   FLOAT_PAT ->
    #     raise SyntaxError
    #   else ->
    #     decSecond  :=  0.0
    #     zoneTail  :=  secondTail ]
    if  secondTail.startswith(':'):
        m = FLOAT_PAT.match(secondTail[1:])
        if  m is None:
            raise SyntaxError("Expecting seconds: '{0}'".format(
                              secondTail))
        else:
            decSecond = float(m.group())
            zoneTail = secondTail[m.end()+1:]
    else:
        decSecond = 0.0
        zoneTail = secondTail
    #-- 4 --
    # [ if zoneTail is empty ->
    #     tz  :=  None
    #   else if zoneTail is a valid zone suffix ->
    #     tz  :=  that zone information as an instance of a class
    #             that inherits from datetime.tzinfo
    #   else -> raise SyntaxError ]
    if  len(zoneTail) == 0:
        tz = None
    else:
        tz = parseZone(zoneTail)
    #-- 5 --
    # [ hours  :=  decHour + decMinute/60.0 + decSecond/3600.0 ]
    hours = float(MixedValue(DMS_UNITS,
                  (decHour, decMinute, decSecond)))/3600.0
    #-- 6 --
    # [ return a datetime.time representing hours ]
    mixTime = MixedValue(DMS_UNITS, hours)
    hh = mixTime.coeffs[0]
    mm = mixTime.coeffs[1]
    wholeSeconds, fracSeconds = divmod(mixTime.coeffs[2], 1.0)
    ss = int(wholeSeconds)
    usec = int(fracSeconds * 1e6)
    return datetime.time(hh, mm, ss, usec, tz)

# - - -   p a r s e Z o n e

def parseZone(s):
    """Validate and convert a time zone suffix.

      [ s is a string ->
          if s is a valid time zone suffix ->
            return that zone's information as an instance of
            a class that inherits from datetime.tzinfo
          else -> raise SyntaxError ]
    """
    #-- 1 --
    # [ if s starts with "+" or "-" and is a valid fixed-offset
    #   time zone suffix ->
    #     return that zone's information as a datetime.tzinfo instance
    #   else if is starts with "+" or "-" but is not a valid
    #   fixed-offset time zone suffix ->
    #     raise SyntaxError
    #   else -> I ]
    if  s.startswith("+") or s.startswith("-"):
        return  parseFixedZone(s)

    #-- 2 --
    # [ if s.upper() is a key in zoneCodeMap ->
    #     return the corresponding value
    #   else -> raise SyntaxError ]
    try:
        tz = zoneCodeMap[s.upper()]
        return tz
    except KeyError:
        raise SyntaxError("Unknown time zone code: '{0}'".format(s))

# - - -   p a r s e F i x e d Z o n e

HHMM_PAT = re.compile (
    r'\d{4}'    # Matches exactly four digits
    r'$')        # Be sure everything is matched

def parseFixedZone(s):
    """Convert a +hhmm or -hhmm zone suffix.

      [ s is a string ->
          if s is a time zone suffix of the form "+hhmm" or "-hhmm" ->
            return that zone information as an instance of a class
            that inherits from datetime.tzinfo
          else -> raise SyntaxError ]
    """
    #-- 1 --
    if  s.startswith('+'):    sign = 1
    elif  s.startswith('-'):  sign = -1
    else:
        raise SyntaxError("Expecting zone modifier as {0}hhmm: "
                          "'{1}'".format(s[0], s))
    #-- 2 --
    # [ if s[1:] matches HHMM_PAT ->
    #     hours  :=  the HH part as an int
    #     minutes  :=  the MM part as an int
    #   else -> raise SyntaxError ]
    rawHHMM = s[1:]
    m = HHMM_PAT.match(rawHHMM)
    if  m is None:
        raise SyntaxError("Expecting zone modifier as {0}HHMM: "
                          "'{1}'".format(s[0], s))
    else:
        hours = int(rawHHMM[:2])
        minutes = int(rawHHMM[2:])

    #-- 3 --
    return  FixedZone(sign*hours, sign*minutes, s)

# - - - - -   c l a s s   F i x e d Z o n e

DELTA_ZERO = datetime.timedelta(0)
DELTA_HOUR = datetime.timedelta(hours=1)

class FixedZone(datetime.tzinfo):
    """Represents a time zone with a fixed offset east of UTC.

      Exports:
        FixedZone(hours, minutes, name):
          [ (hours is a signed offset in hours as an int) and
            (minutes is a signed offset in minutes as an int) ->
              return a new FixedZone instance representing
              those offsets east of UTC ]

      State/Invariants:
        .__offset:
          [ a datetime.timedelta representing self's offset
            east of UTC ]
        .__name:
          [ as passed to the constructor's name argument ]
    """
    def __init__(self, hh, mm, name):
        """Constructor for FixedZone.
        """
        self.__offset = datetime.timedelta(hours=hh, minutes=mm)
        self.__name = name
    def utcoffset(self, dt):
        """Return self's offset east of UTC.
        """
        return  self.__offset
    def  tzname(self, dt):
        """Return self's name.
        """
        return  self.__name
    def  dst(self, dt):
        """Return self's daylight time offset.
        """
        return  DELTA_ZERO
def firstSundayOnOrAfter(dt):
    """Find the first Sunday on or after a given date.

      [ dt is a datetime.date ->
          return a datetime.date representing the first Sunday
          on or after dt ]
    """
    daysToGo = dt.weekday()
    if  daysToGo:
        dt  +=  datetime.timedelta(daysToGo)
    return dt

# - - - - -   c l a s s   U S T i m e Z o n e

class USTimeZone(datetime.tzinfo):
    """Represents a U.S. time zone, with automatic daylight time.

      Exports:
        USTimeZone(hh, mm, name, stdName, dstName):
          [ (hh is an offset east of UTC in hours) and
            (mm is an offset east of UTC in minutes) and
            (name is the composite zone name) and
            (stdName is the non-DST name) and
            (dstName is the DST name) ->
              return a new USTimeZone instance with those values ]

      State/Invariants:
        .__offset:
          [ self's offset east of UTC as a datetime.timedelta ]
        .__name:      [ as passed to constructor's name ]
        .__stdName:   [ as passed to constructor's stdName ]
        .__dstName:   [ as passed to constructor's dstName ]
    """
    DST_START_OLD = datetime.datetime(1, 4, 1, 2)
    DST_END_OLD = datetime.datetime(1, 10, 25, 2)
    DST_START_2007 = datetime.datetime(1, 3, 8, 2)
    DST_END_2007 = datetime.datetime(1, 11, 1, 2)
    def __init__(self, hh, mm, name, stdName, dstName):
        self.__offset  = datetime.timedelta(hours=hh, minutes=mm)
        self.__name    = name
        self.__stdName = stdName
        self.__dstname = dstName
    def tzname(self, dt):
        if  self.dst(dt):   return self.__dstName
        else:               return self.__stdName
    def utcoffset(self, dt):
        return self.__offset + self.dst(dt)
    def dst(self, dt):
        """Return the current DST offset.

          [ dt is a datetime.date ->
              if  daylight time is in effect in self's zone on
              date dt ->
                return +1 hour as a datetime.timedelta
              else ->
                return 0 as a datetime.delta ]
        """
        #-- 1 --
        # [ dtStart  :=  Sunday when DST starts in year dt.year
        #   dtEnd    :=  Sunday when DST ends in year dt.year ]
        if  dt.year >= 2007:
            startDate = self.DST_START_2007.replace(year=dt.year)
            endDate = self.DST_END_2007.replace(year=dt.year)
        else:
            startDate = self.DST_START_OLD.replace(year=dt.year)
            endDate = self.DST_END_OLD.replace(year=dt.year)
        dtStart = firstSundayOnOrAfter(startDate)
        dtEnd   = firstSundayOnOrAfter(endDate)
        #-- 2 --
        # [ naiveDate  :=  dt with its tzinfo member set to None ]
        naiveDate = dt.replace(tzinfo=None)
        #-- 3 --
        # [ if naiveDate is in the interval (dtStart, dtEnd) ->
        #     return DELTA_HOUR
        #   else ->
        #     return DELTA_ZERO ]
        if  dtStart <= naiveDate < dtEnd:
            return  DELTA_HOUR
        else:
            return  DELTA_ZERO
utcZone = FixedZone(0, 0, "UTC")

estZone = FixedZone(-5, 0, "EST")
edtZone = FixedZone(-4, 0, "EDT")
etZone  = USTimeZone(-5, 0, "ET", "EST", "EDT")

cstZone = FixedZone(-6, 0, "CST")
cdtZone = FixedZone(-5, 0, "CDT")
ctZone  = USTimeZone(-6, 0, "CT", "CST", "CDT")

mstZone = FixedZone(-7, 0, "MST")
mdtZone = FixedZone(-6, 0, "MDT")
mtZone  = USTimeZone(-7, 0, "MT", "MST", "MDT")

pstZone = FixedZone(-8, 0, "PST")
pdtZone = FixedZone(-7, 0, "PDT")
ptZone  = USTimeZone(-8, 0, "PT", "PST", "PDT")

zoneCodeMap = {
    "UTC": utcZone,
    "EST": estZone,    "EDT": edtZone,    "ET":  etZone,
    "CST": cstZone,    "CDT": cdtZone,    "CT":  ctZone,
    "MST": mstZone,    "MDT": mdtZone,    "MT":  mtZone,
    "PST": pstZone,    "PDT": pdtZone,    "PT":  ptZone }

# - - -   p a r s e A n g l e

def parseAngle(s):
    """Validate and convert an external angle.

      [ s is a string ->
          if s is a valid external angle ->
            return s in radians
          else -> raise SyntaxError ]
    """
    #-- 1 --
    minute = second = 0.0
    #-- 2 --
    # [ if s starts with a float followed by 'd' or 'D' ->
    #     degree    :=  that float as type float
    #     minTail  :=  s after that float and suffix
    #   else -> raise SyntaxError ]
    degree, minTail = parseFloatSuffix(s, D_PAT,
                          "Degrees followed by 'd'")

    #-- 3 --
    # [ if minTail is empty -> I
    #   else if minTail has the form "(float)m" ->
    #     minute  :=  that (float)
    #   else if minTail has the form "(float)m(float)s" ->
    #     minute  :=  the first (float)
    #     second  :=  the second (float)
    #   else -> raise SyntaxError ]
    if  len(minTail) != 0:
        #-- 3.1 --
        # [ if minTail starts with a float followed by 'm' or 'M' ->
        #     minute  :=  that float as type float
        #     secTail  :=  minTail after all that
        #   else -> raise SyntaxError ]
        minute, secTail = parseFloatSuffix(minTail, M_PAT,
                                "Minutes followed by 'm'")

        #-- 3.2 --
        # [ if secTail is empty -> I
        #   else if secTail starts with a float followed by
        #   's' or 'S' ->
        #     second  :=  that float as type float
        #     checkTail  :=  secTail after all that
        #   else -> raise SyntaxError ]
        if  len(secTail) != 0:
            second, checkTail = parseFloatSuffix(secTail,
                S_PAT, "Seconds followed by 's'")
            if  len(checkTail) != 0:
                raise SyntaxError("Unidentifiable angle parts: "
                                  "'{0}'".format(checkTail))
    #-- 4 --
    # [ return the angle (degree, minute, second) in radians ]
    mixAngle = MixedValue(DMS_UNITS, (degree, minute, second))
    angleDegrees = float(mixAngle)
    return math.radians(angleDegrees)

# - - -   p a r s e F l o a t S u f f i x

def parseFloatSuffix(s, codeRe, message):
    """Parse a float followed by a letter code.

      [ (s is a string) and
        (codeRe is a compiled regular expression) and
        (message is a string describing what is expected) ->
          if  s starts with a float, followed by code (using 
          case-insensitive comparison) ->
            return (x, tail) where x is that float as type float
            and tail is the part of s after the float and code
          else -> raise SyntaxError, "Expecting (message)" ]
    """
    #-- 1 --
    # [ if  s starts with a float ->
    #     x  :=  that float as type float
    #     codeTail  :=  the part of s after that float
    #   else -> raise SyntaxError, "Expecting (message)" ]
    x, codeTail = parseFloat(s, message)

    #-- 2 --
    # [ if codeTail starts with code (case-insensitive) ->
    #     return (x, the part of codeTail after the match)
    #   else -> raise SyntaxError ]
    discard, tail = parseRe(codeTail, codeRe, message)

    #-- 3 --
    return (x, tail)

# - - -   p a r s e F l o a t

def parseFloat(s, message):
    """Parse a floating-point number at the front of s.

      [ (s is a string) and
        (message is a string describing what is expected) ->
          if s begins with a floating-point number ->
            return (x, tail) where x is the number as type float
            and tail is the part of s after the match
          else -> raise SyntaxError, "Expecting (message)" ]
    """
    #-- 1 --
    # [ if the front of s matches FLOAT_PAT ->
    #     m  :=  a Match object describing the match
    #   else -> raise SyntaxError ]
    rawFloat, tail = parseRe(s, FLOAT_PAT, message)

    #-- 2 --
    return  (float(rawFloat), tail)

# - - -   p a r s e R e

def parseRe(s, regex, message):
    """Parse a regular expression at the head of a string.

      [ (s is a string) and
        (regex is a compiled regular expression) and
        (message is a string describing what is expected) ->
          if  s starts with a string that matches regex ->
            return (head, tail) where head is the part of s
            that matched and tail is the rest
          else ->
            raise SyntaxError("Expecting (message)") ]
    """

    #-- 1 --
    # [ if the head of s matches regex ->
    #     m  :=  a match object describing the matching part
    #   else -> raise SyntaxError("Expecting (message)") ]
    m = regex.match(s)
    if  m is None:
        raise SyntaxError("Expecting {0}: '{1}'".format(message, s))
    #-- 2 --
    # [ return (matched text from s, text from s after match) ]
    head = m.group()
    tail = s[m.end():]
    return  (head, tail)

# - - -   p a r s e L a t

def parseLat(s):
    """Validate and convert an external latitude.

      [ s is a nonempty string ->
          if s is a valid external latitude ->
            return that latitude in radians
          else -> raise SyntaxError ]
    """
    #-- 1 --
    # [ last  :=  last character of s
    #   rawAngle  :=  s up to the last character ]
    last = s[-1]
    rawAngle = s[:-1]

    #-- 2 --
    # [ if last matches NS_PAT ->
    #     nsFlag  :=  last, lowercased
    #   else -> raise SyntaxError ]
    m = NS_PAT.match(last)
    if  m is None:
        raise SyntaxError("Latitude '{0}' does not end with 'n' "
                          "or 's'.".format(s))
    else:
        nsFlag = last.lower()
    #-- 3 --
    # [ if rawAngle is a valid angle ->
    #     absAngle  :=  that angle in radians
    #   else -> raise SyntaxError ]
    absAngle = parseAngle(rawAngle)
    #-- 4 --
    if  nsFlag == 's':  angle = - absAngle
    else:               angle = absAngle

    #-- 5 --
    return angle

# - - -   p a r s e L o n

def parseLon(s):
    """Validate and convert an external longitude.

      [ s is a nonempty string ->
          if s is a valid external longitude ->
            return that longitude in radians
          else -> raise SyntaxError ]
    """
    #-- 1 --
    # [ last  :=  last character of s
    #   rawAngle  :=  s up to the last character ]
    last = s[-1]
    rawAngle = s[:-1]

    #-- 2 --
    # [ if EW_PAT matches last ->
    #     ewFlag  :=  last, lowercased
    #   else -> raise SyntaxError ]
    m = EW_PAT.match(last)
    if  m is None:
        raise SyntaxError("Longitude '{0}' does not end with "
                          "'e' or 'w'.".format(s))
    else:
        ewFlag = last.lower()
    #-- 3 --
    # [ if rawAngle is a valid angle ->
    #     absAngle  :=  that angle in radians
    #   else -> raise SyntaxError ]
    absAngle = parseAngle(rawAngle)
    #-- 4 --
    if  ewFlag == 'w':   angle = TWO_PI - absAngle
    else:                angle = absAngle

    #-- 5 --
    return  angle

# - - -   p a r s e H o u r s

def parseHours(s):
    """Validate and convert a quantity in hours.

      [ s is a non-empty string ->
          if s is a valid mixed hours expression ->
            return the value of s as decimal hours
          else -> raise SyntaxError ]
    """
    #-- 1 --
    minute = second = 0.0

    #-- 2 --
    # [ if s starts with a float followed by 'h' or 'H' ->
    #     hour  :=  that float as type float
    #     minTail  :=  s after that float and suffix
    #   else -> raise SyntaxError ]
    hour, minTail = parseFloatSuffix(s, H_PAT,
                          "Hours followed by 'h'")

    #-- 3 --
    # [ if minTail is empty -> I
    #   else if minTail has the form "(float)m" ->
    #     minute  :=  that (float)
    #   else if minTail has the form "(float)m(float)s" ->
    #     minute  :=  the first (float)
    #     second  :=  the second (float)
    #   else -> raise SyntaxError ]
    if  len(minTail) != 0:
        #-- 3.1 --
        # [ if minTail starts with a float followed by 'm' or 'M' ->
        #     minute  :=  that float as type float
        #     secTail  :=  minTail after all that
        #   else -> raise SyntaxError ]
        minute, secTail = parseFloatSuffix(minTail, M_PAT,
                                "Minutes followed by 'm'")

        #-- 3.2 --
        # [ if secTail is empty -> I
        #   else if secTail starts with a float followed by
        #   's' or 'S' ->
        #     second  :=  that float as type float
        #     checkTail  :=  secTail after all that
        #   else -> raise SyntaxError ]
        if  len(secTail) != 0:
            second, checkTail = parseFloatSuffix(secTail,
                S_PAT, "Seconds followed by 's'")
            if  len(checkTail) != 0:
                raise SyntaxError("Unidentifiable angle parts: "
                                  "'{0}'".format(checkTail))
    #-- 4 --
    # [ return the quantity (hour, minute, second) in hours ]
    mixTime = MixedValue(DMS_UNITS, (hour, minute, second))
    return float(mixTime)

# - - - - -   c l a s s   M i x e d V a l u e

class MixedValue(object):
    """Represents a system with mixed units, e.g., hours/minutes/seconds

      Exports:
        MixedValue(factorList, coeffs):
          [ P: factorList is a sequence of relative weights such as
               (24, 60, 60) for the days-hours-minutes-seconds system,
               or a single scalar value for a two-valued system
            P: coeffs is a sequence of scalar numbers representing
               coefficients in this number system, or a single scalar
               number, with implied right zero fill to size
               len(factorList)+1
            return a new MixedValue instance representing those values ]
        .factorList:              [ as passed to constructor, read-only ]
        .coeffs:
          [ a list containing the (coeffs) passed to the constructor,
            with right zero fill to size len(factorList)+1, normalized
            so that all values but the last are int, and the last is
            an int or float ]
        .__float__(self):
          [ return self as a float expressed in the largest factors ]
        .format(decimals=0, lz=False):
          [ return the coefficients in self as a list of strings,
            with the last value showing (decimals) digits after the
            decimal, and each integral part left-zero-padded based
            on the corresponding (factorList) element iff (lz) ]
      State/Invariants:
        .weightList:
          [ a list of ints, of length len(self.factorList)+1,
            such that weightList[k] is the product of all
            elements of factorList[k:] ]
        .digitsList:
          [ a list of length len(self.factorList), such that
            self.digitsList[k] is the number of digits in
            the corresponding element of self.factorList ]
    """

# - - -   M i x e d V a l u e . _ _ i n i t _ _

    def __init__(self, factorList, rawCoeffs):
        """Constructor
        """
        #-- 1
        # [ if factorList is a sequence ->
        #     self.factorList  :=  copy of factorList as a tuple
        #   else ->
        #     self.factorList  :=  [factorList] ]
        if '__getitem__' in dir(factorList):
            self.factorList = tuple(factorList[:])
        else:
            self.factorList = (factorList,)
        #-- 2
        # [ if rawCoeffs is a sequence ->
        #     coeffs  :=  copy of rawCoeffs as a list
        #   else ->
        #     coeffs  :=  [rawCoeffs] ]
        if '__getitem__' in dir(rawCoeffs):
            coeffs = rawCoeffs[:]
        else:
            coeffs = [rawCoeffs]
        #-- 3
        #   self.coeffs  :=  (a list containing len(factorList)
        #       int zeroes) + [0.0]
        #   self.weightList  :=  as invariant
        #   self.digitsList  :=  as invariant ]
        self.coeffs = [0]*len(self.factorList) + [0.0]
        self.weightList = [1]
        self.digitsList = []
        weight = 1
        for factor in reversed(self.factorList):
            self.weightList.insert(0, factor * weight)
            weight *= factor
            self.digitsList.insert(0, len(str(factor)))
        #-- 4
        # [ if len(coeffs) <= len(self.factorList) + 1 ->
        #    self.coeffs  :=  self.coeffs with corresponding values of
        #        coeffs added
        #   else -> raise ValueError ]
        maxFactors = len(self.factorList) + 1
        if len(coeffs) <= maxFactors:
            for k in range(len(coeffs)):
                self.coeffs[k] += coeffs[k]
        else:
            raise ValueError("Too many coefficients ({0}): "
                "limit {1}".format(len(coeffs), maxFactors))
        #-- 5
        # [ self.coeffs  :=  self.coeffs normalized ]
        self.normalize()

# - - -   M i x e d V a l u e . n o r m a l i z e

    def normalize(self):
        '''Push fractional parts of nonlast coefficients down.

          [ self.coeffs  :=  self.coeffs normalized, that is, with all
                elements but the last integral, without changing self's
                value in the positional system ]
        '''
        #-- 1
        # [ coeffs  :=  coeffs with all elements but the last
        #       integral, without changing the value of self ]
        for k in range(len(self.factorList)):
            w, f = divmod(self.coeffs[k], 1.0)
            self.coeffs[k] = int(w)
            self.coeffs[k+1] += f * self.factorList[k]

        #-- 2
        # [ coeffs  :=  coeffs with all elements but the last
        #       integral and the last element less than the
        #       last element of factorlist, without changing self's
        #       value in the positional system ]
        for k in range(len(self.factorList), 0, -1):
            w, f = divmod(self.coeffs[k], self.factorList[k-1])
            self.coeffs[k] = f
            self.coeffs[k-1] += int(w)

# - - -   M i x e d V a l u e . _ _ f l o a t _ _

    def __float__(self):
        '''Return self as a float.
        '''
        #-- 1
        return sum([self.coeffs[k] * self.weightList[k]
                    for k in range(len(self.coeffs))])

# - - -   M i x e d V a l u e . _ _ a d d _ _

    def __add__(m1, m2):
        '''Sum of two MixedValue instances.
        '''
        #-- 1
        newCoeffs = [m1.coeffs[k] + m2.coeffs[k]
                     for k in range(len(m1.coeffs))]

        #-- 2
        return MixedValue(m1.factorList, newCoeffs)

# - - -   M i x e d V a l u e . f o r m a t

    def format(self, decimals=0, lz=False):
        '''Format with fuzz
        '''
        #-- 1
        if lz:
            intFormat = "{0:0{w}d}"
            floatFormat = "{0:0{w}.{p}f}"
        else:
            intFormat = "{0:{w}d}"
            floatFormat = "{0:{w}.{p}f}"

        #-- 2
        result = [str(self.coeffs[0])]

        #-- 3
        # [ result  +:=  a list made by formatting self.coeffs[1:-1]
        #       with intFormat, using w=self.digitsList[k-1] ]
        result += [intFormat.format(self.coeffs[k],
                                    w=self.digitsList[k-1])
                  for k in range(1, len(self.factorList))]
        #-- 3
        lastCo = float(self.coeffs[-1])
        whole, frac = divmod(lastCo, 1.0)
        fuzz = 0.5 * (10.0 ** (-decimals))

        #-- 4
        if frac >= (1.0-fuzz):
            corrected = whole + frac - fuzz
        else:
            corrected = lastCo
        #-- 5
        if decimals > 0:
            wide = self.digitsList[-1] + 1 + decimals
        else:
            wide = self.digitsList[-1]
        result.append(floatFormat.format(corrected, w=wide,
                      p=decimals))

        #-- 6
        return result

# - - - - -   c l a s s   L a t L o n

class LatLon(object):
    """Represents a latitude+longitude.

      Exports:
        LatLon(lat, lon):
          [ P: latRad is a latitude in radians
            P: lonRad is a longitude in radians
            return a new LatLon instance with latitude (latRad) and
            longitude (lonRad) ]
        .lat:                [ as passed to constructor, read-only ]
        .lon:                [ as passed to constructor, read-only ]
        .__str__(self):
          [ return a string representation of self ]
    """

# - - -  L a t L o n . _ _ i n i t _ _

    def __init__(self, lat, lon):
        """Constructor for LatLon.
        """
        self.lat = lat
        self.lon = lon % TWO_PI

# - - -   L a t L o n . _ _ s t r _ _

    def __str__(self):
        """Return self as a string.
        """
        #-- 1 --
        if  self.lon >= math.pi:
            e_w = "W"
            lonDeg = math.degrees(TWO_PI - self.lon)
        else:
            e_w = "E"
            lonDeg = math.degrees(self.lon)

        #-- 2 --
        if  self.lat < 0:
            n_s = "S"
            latDeg = math.degrees(- self.lat)
        else:
            n_s = "N"
            latDeg = math.degrees(self.lat)
        #-- 3 --
        # [ latList  :=  three formatted values of latDeg in
        #                degrees/minutes/seconds
        #   lonList  :=  three formatted values of lonDeg similarly ]
        mixLat = MixedValue(DMS_UNITS, latDeg)
        latList = mixLat.format(1)
        mixLon = MixedValue(DMS_UNITS, lonDeg)
        lonList = mixLon.format(1)

        #-- 4 --
        return('[{lat[0]}d {lat[1]}\' {lat[2]}" {ns} Lat '
               '{lon[0]}d {lon[1]}\' {lon[2]}" {ew} Lon]'.format(
               lat=latList, ns=n_s, lon=lonList, ew=e_w))

# - - - - -   c l a s s   J u l i a n D a t e

class JulianDate(object):
    """Class to represent Julian-date timestamps.

      Exports:
        JulianDate(j, f=0.0):
          [ P: j is a Julian date as an int or float
            P: f is a fractional day as a float
            return a new JulianDate representing Julian date j+f ]
        .j:
          [ integral part of (j passed to constructor) -
            JULIAN_BIAS + (f passed to constructor)
        .f:
          [ fractional part of (j passed to constructor) -
            JULIAN_BIAS + (f passed to constructor)
        .__float__(self):
          [ return self as a float ]
        .datetime():
          [ return self as a datetime.datetime instance ]
        .offset(nDays):
          [ P: nDays is an integer
            return a new JulianDate representing (nDays) days
            after self ]
        .__sub__(j1, j2):
          [ P: j1 and j2 are JulianDate instances
            return (j1-j2) in days as a float ]
        .__cmp__(j1, j2):
          [ orders instances in ascending chronological order ]
        JulianDate.fromDatetime(dt):    # Static method
          [ P: dt is a datetime.datetime
            return a JulianDate representing dt ]
    """

# - - -   J u l i a n D a t e . _ _ i n i t _ _

    def __init__(self, j, f=0.0):
        """Constructor for JulianDate.
        """
        mixDate = MixedValue(1.0, (j - JULIAN_BIAS, f))
        self.j, self.f = mixDate.coeffs

# - - -   J u l i a n D a t e . _ _ f l o a t _ _

    def __float__(self):
        """Convert self to a float.
        """
        return  self.j + JULIAN_BIAS + self.f

# - - -   J u l i a n D a t e . d a t e t i m e

    def datetime(self):
        """Convert to a standard Python datetime object in UT.
        """
        #-- 1
        # [ mjd  :=  an MJD instance equivalent to self ]
        mjd = MJD(self.j, self.f - 0.5)

        #-- 2
        # [ return mjd as a datetime.datetime ]
        return mjd.datetime()

# - - -   J u l i a n D a t e . o f f s e t

    def offset(self, delta):
        """Return a new JulianDate for self+(delta days)

          [ delta is a number of days as a float ->
              return a new JulianDate (delta) days in the
              future, or past if negative ]
        """
        #-- 1 --
        newJ = self.j + delta

        #-- 2 --
        # [ newWhole  :=  whole part of newJ
        #   newFrac   :=  fractional part of newJ ]
        newWhole, newFrac = divmod(newJ)

        #-- 3 --
        return  JulianDate(newWhole+JULIAN_BIAS, newFrac)

# - - -   J u l i a n D a t e . _ _ s u b _ _

    def __sub__(m1, m2):
        """Implement subtraction.

          [ other is a JulianDate instance ->
              return m1 - m2 as a float in days ]
        """
        diff = MixedValue(1.0, (m2.m - m1.m, m2.f - m1.f))
        return sum(diff.coeffs)

# - - -   J u l i a n D a t e . _ _ c m p _ _

    def __cmp__(m1, m2):
        """Compare two instances.

          [ other is a JulianDate instance ->
              if  m1 < m2 -> return a negative number
              else if m1 == m2 -> return zero
              else -> return a positive number ]
        """
        return cmp((m1.j, m1.f),
                   (m2.j, m2.f))

# - - -   J u l i a n D a t e . f r o m D a t e t i m e

    @staticmethod
    def fromDatetime(dt):
        """Create a JulianDate instance from a datetime.datetime.

          [ dt is a datetime.datetime instance ->
              if  dt is naive ->
                return the equivalent new JulianDate instance,
                assuming dt expresses UTC
              else ->
                return a new JulianDate instance for the UTC
                time equivalent to dt ]              
        """
        #-- 1
        # [ mjd  :=  dt as an MJD instance ]
        mjd = MJD.fromDatetime(dt)

        #-- 2
        # [ return mjd as a JulianDate ]
        return JulianDate(mjd.m + JULIAN_BIAS, mjd.f + 0.5)

# - - - - -   c l a s s   M J D

class MJD(object):
    '''Represents a modified Julian date.

      Exports:
        MJD(m, f=None):
          [ P: j is a Julian date as an int or float
            P: f is a fractional day as a float, defaulting to 0.0
            return a new MJD representing Julian date j+f ]
        .m:
          [ integral part of (m as passed to constructor) +
            (f as passed to constructor, default 0.0) ]
        .f:
          [ fractional part of (m as passed to constructor) +
            (f as passed to constructor, default 0.0) ]
        .__float__(self):
          [ return self as a float ]
        .datetime():
          [ return self as a datetime.datetime instance ]
        .offset(nDays):
          [ P: nDays is an integer
            return a new MJD representing (nDays) days after self ]
        .__sub__(m1, m2):
          [ P: m1 and m2 are MJD instances
            return (m1-m2) in days as a float ]
        .__cmp__(m1, m2):
          [ orders instances in ascending chronological order ]
        MJD.fromDatetime(dt):    # Static method
          [ P: dt is a datetime.datetime
            return a MJD representing dt ]
    '''

# - - -   M J D . _ _ i n i t _ _

    def __init__(self, m, f=None):
        '''Constructor.
        '''
        #-- 1
        if f is None:
            f = 0.0

        #-- 2
        # [ self.m  :=  integral part of m+f
        #   self.f  :=  fractional part of m+f ]
        mix = MixedValue(1.0, (m,f))
        self.m, self.f = mix.coeffs

# - - -   M J D . _ _ f l o a t _ _

    def __float__(self):
        '''Convert to float.
        '''
        return self.m + self.f

# - - -   M J D . d a t e t i m e

    def datetime(self):
        """Convert to a standard Python datetime object in UT.
        """
        #-- 1
        # [ i  :=  int(self.m + JULIAN_BIAS + self.f + 1)
        #   f  :=  (self.m + self.f + 1) % 1.0 ]
        i, f = divmod(self.m + 1.0 + self.f, 1.0)
        i += JULIAN_BIAS
        #-- 2 --
        if  i > 2299160:
            a = int((i-1867216.25)/36524.25)
            b = i + 1 + a - int(a / 4.0)
        else:
            b = i
        #-- 3 --
        c = b + 1524
        #-- 4 --
        d = int((c-122.1)/365.25)
        #-- 5 --
        e = int(365.25*d)
        #-- 6 --
        g = int((c-e)/30.6001)
        #-- 7 --
        dayFrac = c - e + f - int(30.6001 * g)
        day, frac = divmod(dayFrac, 1.0)
        dd = int(day)
        mixDay = MixedValue(DMS_UNITS, 24.0*frac)
        hr, mn, sc = mixDay.coeffs
        #-- 8 --
        if  g < 13.5:  mm = int(g - 1)
        else:             mm = int(g - 13)
        #-- 9 --
        if  mm > 2.5:  yyyy = int(d-4716)
        else:          yyyy = int(d-4715)
        #-- 10 --
        sec, fracSec = divmod(sc, 1.0)
        usec = int(fracSec * 1e6)
        return datetime.datetime(yyyy, mm, dd, hr, mn, int(sec),
                                   usec)

# - - -   M J D . o f f s e t

    def offset(self, delta):
        '''Return a new MJD equal to self plus delta.
        '''
        return MJD(self.m + delta, self.f)

# - - -   M J D . _ _ s u b _ _

    def __sub__(m1, m2):
        """Implement subtraction.

          [ other is a MJD instance ->
              return m1 - m2 as a float in days ]
        """
        diff = MixedValue(1.0, (m1.m - m2.m, m1.f - m2.f))
        return sum(diff.coeffs)

# - - -   M J D . f r o m D a t e t i m e

    @staticmethod
    def fromDatetime(dt):
        """Create an MJD instance from a datetime.datetime.

          [ dt is a datetime.datetime instance ->
              if  dt is naive ->
                return the equivalent new MJD instance, assuming
                dt expresses UTC
              else ->
                return a new MJD instance for the UTC time equivalent
                to dt ]              
        """
        #-- 1 --
        # [ if dt is naive ->
        #     utc  :=  dt
        #   else ->
        #     utc  :=  dt - dt.utcoffset() ]
        utc = dt
        offset = dt.utcoffset()
        if  offset:
            utc = dt - offset
        #-- 2 --
        # [ fracDay  :=  fraction of a day in [0.0,1.0) made from
        #       utc.hour, utc.minute, utc.second, and utc.microsecond ]
        s = float(utc.second) + float(utc.microsecond)*1e-6
        mix = MixedValue(DMS_UNITS, (utc.hour, utc.minute, s))
        seconds = float(mix)
        fracDay = seconds / 86400
        #-- 3 --
        y = utc.year
        m = utc.month
        d = utc.day
        #-- 4 --
        if  m <= 2:
            y, m = y-1, m+12
        #-- 5 --
        if ((y, m, d) >= (1582, 10, 15)):
            A = int(y / 100)
            B = 2 - A + int(A / 4)
        else:
            B = 0
        #-- 6 --
        C = int(365.25 * y)
        D = int(30.6001 *(m + 1))
        #-- 7 --
        m = B + C + D + d - 679006

        #-- 8 --
        return MJD(m, fracDay)
#
# - - - - -   c l a s s   S i d e r e a l T i m e

class SiderealTime(object):
    """Represents a sidereal time value.

      State/Internals:
        .hours:     [ self as 15-degree hours ]
        .radians:   [ self as radians ]
    """

# - - -   S i d e r e a l T i m e . _ _ i n i t _ _

    def __init__(self, hours):
        """Constructor for SiderealTime
        """
        self.hours = hours % 24.0
        self.radians = hoursToRadians(self.hours)

# - - -   S i d e r e a l T i m e . _ _ s t r _ _

    def __str__(self):
        """Convert to a string such as "[04h 40m 5.170s]".
        """

        #-- 1 --
        # [ values  :=  self.hours as a list of mixed units
        #       in DMS_UNITS terms, formatted as left-zero
        #       filled strings with 3 digits after the decimal ]
        hours = MixedValue(DMS_UNITS, self.hours)
        values = hours.format(decimals=3, lz=True)

        #-- 2 --
        return "[{v[0]}h {v[1]}m {v[2]}s]".format(v=values)

# - - -   S i d e r e a l T i m e . u t c

    def utc(self, date):
        """Convert GST to UTC.

          [ date is a UTC date as a datetime.date instance ->
              return the first or only time at which self's GST
              occurs at longitude 0 ]
        """
        #-- 1 --
        # [ nDays  :=  number of days between Jan. 0 of year
        #       (date.year) and date ]
        nDays = dayNo(date)
        #-- 2 --
        # [ t0  :=  (nDays * A - B(date.year)), normalized to
        #           interval [0,24) ]
        t0  = (( nDays * SIDEREAL_A -
                   SiderealTime.factorB(date.year)) % 24.0)
        #-- 3 --
        # [ t1  :=  ((self in decimal hours)-t0), normalized to
        #           the interval [0,24) ]
        t1  = (radiansToHours(self.radians) - t0) % 24.0
        #-- 4 --
        gmtHours = t1 * 0.997270
        #-- 5 --
        # [ dt  :=  a datetime.datetime instance whose date comes
        #           from (date) and whose time is (gmtHours)
        #           decimal hours ]
        mixGmt = MixedValue(DMS_UNITS, gmtHours)
        hour, minute, floatSec = mixGmt.coeffs
        wholeSec, fracSec = divmod(floatSec, 1.0)
        second = int(wholeSec)
        micros = int(fracSec * 1e6)
        dt = datetime.datetime(date.year, date.month,
                   date.day, hour, minute, second, micros)
        
        #-- 6 --
        return  dt

# - - -   S i d e r e a l T i m e . f a c t o r B

    @staticmethod
    def factorB(yyyy):
        """Compute sidereal conversion factor B for a given year.

          [ yyyy is a year number as an int ->
              return the GST at time yyyy-01-00T00:00 ]
        """
        #-- 1 --
        # [ janJD  :=  the Julian date of January 0.0 of year
        #              (yyyy), as a float ]
        janDT = datetime.datetime(yyyy, 1, 1)
        janJD = float(JulianDate.fromDatetime(janDT)) - 1.0
        #-- 2 --
        s = janJD - 2415020.0

        #-- 3 --
        t = s / 36525.0

        #-- 4 --
        r  = (0.00002581 * t +
                2400.051262) * t + 6.6460656
        #-- 5 --
        u = r - 24 *(yyyy-1900)

        #-- 6 --
        return 24.0 - u

# - - -   S i d e r e a l T i m e . g s t

    def gst(self, eLong):
        """Convert LST to GST.

          [ self is local sidereal time at longitude eLong
            radians east of Greenwich ->
              return the equivalent GST as a SiderealTime instance ]
        """
        #-- 1 --
        # [ deltaHours  :=  eLong expressed in hours ]
        deltaHours = radiansToHours(eLong)

        #-- 2 --
        gstHours  = (self.hours - deltaHours) % 24.0

        #-- 3 --
        return SiderealTime(gstHours)

# - - -   S i d e r e a l T i m e . l s t

    def lst(self, eLong):
        """Convert GST to LST.

          [ (self is Greenwich sidereal time) and
            (eLong is a longitude east of Greenwich in radians) ->
              return a new SiderealTime representing the LST
              at longitude eLong ]
        """
        #-- 1 --
        # [ deltaHours  :=  eLong expressed in hours ]
        deltaHours = radiansToHours(eLong)

        #-- 2 --
        gmtHours = (self.hours + deltaHours) % 24.0

        #-- 3 --
        return SiderealTime(gmtHours)

# - - -   S i d e r e a l T i m e . f r o m D a t e t i m e

    SIDEREAL_C = 1.002738

    @staticmethod
    def fromDatetime(dt):
        """Convert civil time to Greenwich Sidereal.

          [ dt is a datetime.datetime instance ->
              if  dt has time zone information ->
                return the GST at the UTC equivalent to dt
              else ->
                return the GST assuming dt is UTC ]
        """
        #-- 1 --
        # [ if  dt is naive ->
        #     utc  :=  dt
        #   else ->
        #     utc  :=  the UTC time equivalent to dt ]
        utc = dt
        tz = dt.tzinfo
        if  tz is not None:
            offset = tz.utcoffset(dt)
            if  offset is not None:
                utc = dt - offset
        #-- 2 --
        # [ nDays  :=  number of days between January 0.0 and utc ]
        nDays = dayNo(utc)
        #-- 3 --
        t0  = (nDays * SIDEREAL_A -
                 SiderealTime.factorB(utc.year))
        #-- 4 --
        # [ decUTC  :=  utc as decimal hours ]
        floatSec = utc.second + float(utc.microsecond) / 1e6
        mixUTC = MixedValue(DMS_UNITS,
                            (utc.hour, utc.minute, floatSec))        
        decUTC = float(mixUTC) / 3600
        #-- 4 --
        # [ gst  :=  (decUTC * C + t0), normalized to interval [0,24) ]
        gst  = (decUTC * SiderealTime.SIDEREAL_C + t0) % 24.0

        #-- 5 --
        return SiderealTime(gst)

# - - - - -   c l a s s   A l t A z

class AltAz(object):
    """Represents a sky location in horizon coords. (altitude/azimuth)

      Exports/Invariants:
        .alt:   [ altitude in radians, in [-pi,+pi] ]
        .az:    [ azimuth in radians, in [0,2*pi] ]
    """

# - - -   A l t A z . _ _ i n i t _ _

    def __init__(self, alt, az):
        """Constructor for AltAz, horizon coordinates.

          [ (alt is an altitude in radians) and
            (az is an azimuth in radians) ->
              return a new AltAz instance with those values,
              normalized as per class invariants ]
        """
        self.alt = alt
        self.az = az

# - - -   A l t A z . r a D e c

    def raDec(self, lst, latLon):
        """Convert horizon coordinates to equatorial.

          [ (lst is a local sidereal time as a SiderealTime instance) and
            (latLon is the observer's position as a LatLon instance) ->
              return the corresponding equatorial coordinates as a
              RADec instance ]            
        """
        #-- 1 --
        # [ dec  :=  declination of self at latLon in radians
        #   hourRadians  :=  hour angle of self at latlon in radians ]
        dec, hourRadians = coordRotate(self.alt, latLon.lat, self.az)

        #-- 2 --
        # [ hourRadians is an hour angle in radians ->
        #     h  :=  hourRadians in hours ]
        h = radiansToHours(hourRadians)
        #-- 3 --
        # [ ra  :=  right ascension for hour angle (h) at local
        #           sidereal time (lst) and location (latLon) ]
        ra = hoursToRadians(( lst.hours - h) % 24.0)

        #-- 4 --
        return  RADec(ra, dec)

# - - -   A l t A z . _ _ s t r _ _

    def __str__(self):
        """Convert self to a string.
        """
        #-- 1 --
        # [ altList  :=  self.alt, formatted as degrees, minutes,
        #       and seconds
        #   azList  :=  self.az, formatted as degrees, minutes, and
        #       seconds ]
        altMix = MixedValue(DMS_UNITS, math.degrees(self.alt))
        altList = altMix.format(3, True)
        azMix = MixedValue(DMS_UNITS, math.degrees(self.az))
        azList = azMix.format(3, True)

        #-- 2 --
        return ("[az {az[0]}d {az[1]}' {az[2]}\" "
                "alt {alt[0]}d {alt[1]}' {alt[2]}\"]".format(
                az=azList, alt=altList))

# - - -   c o o r d R o t a t e

def coordRotate(x, y, z):
    """Used to convert between equatorial and horizon coordinates.

      [ x, y, and z are angles in radians ->
          return (xt, yt) where
          xt=arcsin(sin(x)*sin(y)+cos(x)*cos(y)*cos(z)) and
          yt=arccos((sin(x)-sin(y)*sin(xt))/(cos(y)*cos(xt))) ]
    """
    #-- 1 --
    xt = math.asin(math.sin(x) * math.sin(y) +
                   math.cos(x) * math.cos(y) * math.cos(z))
    #-- 2 --
    yt = math.acos((math.sin(x) - math.sin(y) * math.sin(xt)) /
                   (math.cos(y) * math.cos(xt)))
    #-- 3 --
    if  math.sin(z) > 0.0:
        yt = TWO_PI - yt

    #-- 4 --
    return (xt, yt)

# - - - - -   c l a s s   R A D e c

class RADec(object):
    """Represents a celestial location in equatorial coordinates.

      Exports/Invariants:
        .ra:      [ right ascension in radians ]
        .dec:     [ declination in radians ]
    """

# - - -   R A D e c . _ _ i n i t _ _

    def __init__(self, ra, dec):
        """Constructor for RADec.
        """
        self.ra = ra % TWO_PI
        self.dec = dec

# - - -   R A D e c . h o u r A n g l e

    def hourAngle(self, utc, eLong):
        """Find the hour angle at a given observer's location.

          [ (utc is a Universal Time as a datetime.datetime) and
            (eLong is an east longitude in radians) ->
              return the hour angle of self at that time and
              longitude, in radians ]
        """
        return  raToHourAngle(self.ra, utc, eLong)

# - - -   R A D e c . a l t A z

    def altAz(self, h, lat):
        """Convert equatorial to horizon coordinates.

          [ (h is an object's hour angle in radians) and
            (lat is the observer's latitude in radians) ->
              return self's position in the observer's sky
              in horizon coordinates as an AltAz instance ]
        """
        #-- 1 --
        # [ alt  :=  altitude of self as seen from latLon at utc
        #   az  :=  azimuth of self as seen from latLon at utc ]
        alt, az = coordRotate(self.dec, lat, h)

        #-- 2 --
        return AltAz(alt, az)

# - - -   R A D e c . _ _ s t r _ _

    def __str__(self):
        """Return self as a string.
        """
        #-- 1 --
        # [ raUnits  :=  units of self.ra as hours/minutes/seconds
        #   decUnits  :=  units of self.dec as degrees/minutes/seconds
        raMix = MixedValue(DMS_UNITS, radiansToHours(self.ra))
        raUnits = raMix.format(3, True)
        decMix = MixedValue(DMS_UNITS, math.degrees(self.dec))
        decUnits = decMix.format(3, True)

        #-- 2 --
        return("[{ra[0]}h {ra[1]}m {ra[2]}s, "
               "{dec[0]}d {dec[1]}' {dec[2]}\"]".format(
               ra=raUnits, dec=decUnits))


