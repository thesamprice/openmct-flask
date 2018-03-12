import ctypes

"Hey this supports big endian packets"
my_endian=ctypes.BigEndianStructure



class CCSDS_PriHdr_t_StreamId (my_endian):
    """Some comments"""
    _pack_ = 1
    _fields_ = [ ("packet_version_number"    , ctypes.c_ushort ,3),
                 ("packet_type"              , ctypes.c_ushort ,1),
                 ("secondary_header_present" , ctypes.c_ushort ,1),
                 ("apid"                     , ctypes.c_ushort ,11)]


class CCSDS_PriHdr_t_Sequence (my_endian):
    """Some comments"""
    _pack_ = 1
    _fields_ = [ ("sequence_flags" , ctypes.c_ushort ,2),
                 ("sequence_count" , ctypes.c_ushort ,14)]


class CCSDS_PriHdr_t (my_endian):
    """
CCSDS_PriHdr_t{
    /*!
    *@bitarray msbf
    *  @bits 3
    *    @name packet_version_number
    *    @brief Pacet Version Number
    *    @default 0
    *  @bits 1
    *    @name packet_type
    *    @brief Packet type, 0=TLM, 1 = CMD
    *  @bits 1
    *    @name secondary_header_present
    *    @brief Secondary Header flag
    *    @detailed The Secondary Header Flag shall indicate the presence or absence of the Packet Secondary Header within this Space Packet.
    *    It shall be 1 if a Packet Secondary Header is present; it shall be 0 if a Packet Secondary Header is not present.
    *    0 = absent, 1 = present
    *  @bits 11
    *    @name apid
    *    @brief Application Process Identifier (APID)
    *    @detailed  via 135.0-b-1 application ID's 2040- 2047 are reserved and should not be used.
    *    The APID (possibly in conjunction with the optional APID Qualifier that
    *    identifies the naming domain for the APID) shall provide the naming mechanism for the LDP.
    */
   uint16  StreamId;     /* packet identifier word (stream ID) */

   /*!
   *@bitarray msbf
   *  @bits 2
   *    @name sequence_flags
   *    @brief 3 = complete packet
   *  @bits 14
   *    @name sequence_count
   *    @brief  Packet Sequence Count
   */
   uint16  Sequence;     /* packet sequence word */

   /*!
    * @brief The Packet data length. Total number of octets in packet data field - 1
    */
   uint16  Length;
} """
    _pack_ = 1

    _fields_ = [ ("StreamId" , CCSDS_PriHdr_t_StreamId ),
                 ("Sequence" , CCSDS_PriHdr_t_Sequence ),
                 ("Length"   , ctypes.c_ushort )]
    def SetConstants(self):
        pass


class CCSDS_Telemetry_Header (my_endian):
    """/*!
 *  @brief CCSDS Telemetry Header
 *  @TelemetryPacketHeader
 *
 */
CCSDS_Telemetry_Header
{
    CCSDS_PriHdr_t Pri;

    /*
    *@bitarray msbf
    *  @bits 1
    *    @name ccsds_standard_secondary_header
    *    @enum CCSDS_Standard_Secondary_header
    *  @bits 63
    *    @name time_stamp
    *    @brief It is the intent to have this data populated by C&DH to mark the S/C time at which the packet was received.
    */
    int8 s_time[8];


} """
    _pack_ = 1

    _fields_ = [ ("Pri"       , CCSDS_PriHdr_t ),
                 ("s_time"    , ctypes.c_byte * 8 )]
    def SetConstants(self):
        pass



class SPS_M_time_ws (my_endian):
    """Some comments"""
    _pack_ = 1
    _fields_ = [ ("week_hw" , ctypes.c_uint ,12),
                 ("sec_hw"  , ctypes.c_uint ,20)]


class SPS_M (my_endian):
    """Basic Point soltuion packet """
    _pack_ = 1
    _tlm_  = 1
    _apid_ = 4
    _fields_ = [ ("packet_header"    , CCSDS_Telemetry_Header ),
                 ("time_ws"          , SPS_M_time_ws ),
                 ("time_sub"         , ctypes.c_uint ),
                 ("x"                , ctypes.c_double ),
                 ("y"                , ctypes.c_double ),
                 ("z"                , ctypes.c_double ),
                 ("vx"               , ctypes.c_double ),
                 ("vy"               , ctypes.c_double ),
                 ("vz"               , ctypes.c_double ),
                 ("time"             , ctypes.c_double ),
                 ("total_bias"       , ctypes.c_double ),
                 ("clock_bias"       , ctypes.c_double ),
                 ("clock_rate"       , ctypes.c_double )]
    def SetConstants(self):
        self.packet_header.Pri.StreamId.apid = 4

class Example_M (my_endian):
    """Basic Point soltuion packet """
    _pack_ = 1
    _tlm_  = 1
    _apid_ = 5
    _fields_ = [ ("packet_header"    , CCSDS_Telemetry_Header ),
                 ("time_ws"          , SPS_M_time_ws ),
                 ("time_sub"         , ctypes.c_uint ),
                 ("temp_a"           , ctypes.c_float ),
                 ("temp_b"           , ctypes.c_int32 ),
                 ("temp_c"           , ctypes.c_int16 * 5 ),
                 ("temp_d"           , ctypes.c_int8 ),
                 ("hello", ctypes.c_double)]
    def SetConstants(self):
        self.packet_header.Pri.StreamId.apid = 5

