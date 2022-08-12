// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;
// This is the smart Contract
contract log {
    string[] public log_data;
    string[] public time_stamp;
    string[] public user_id;
    string[] public file_name;
    int public count = 0;


    function build(string memory _log_data,string memory _time_stamp,string memory _uid, string memory _file_name) public {
        setLogData(_log_data);
        setTimeStamp(_time_stamp);
        setUserId(_uid);
        setFileName(_file_name);
        count = count + 1;
    }

    function setLogData (string memory _log_data) public {
        log_data.push(_log_data);
    }

    function setTimeStamp(string memory _time_stamp) public {
        time_stamp.push(_time_stamp);
    }

    function setUserId(string memory _uid) public {
        user_id.push(_uid);
    }

    function setFileName(string memory _file_name) public {
        file_name.push(_file_name);
    }

}
