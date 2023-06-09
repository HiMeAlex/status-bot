use std::{env, process};
// use std::fs;
use regex::Regex;
use std::net::TcpStream;
use craftping::sync::ping;
// use serde_json::{Value, json};
use std::io::{self, Write};

fn main() -> io::Result<()> {
    let args: Vec<String> = env::args().collect();
    let ip_regex = Regex::new(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$").unwrap();
    let port_regex = Regex::new(r"^([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$").unwrap();
    let stdout = io::stdout();
    let mut handle = stdout.lock();
    
    if args.len() >= 3 {
        if ip_regex.is_match(&args[1]) && port_regex.is_match(&args[2]){
            let ip: &str = &args[1];
            let port: u16 = args[2].parse().unwrap();
            let pid = process::id();
            let _pid_str = format!("{pid}");

            if mcping(ip, port) {
                handle.write_all(b"0")?;
                Ok(())
            } else {
                handle.write_all(b"1")?;
                Ok(())
            }
        } else {
            handle.write_all(b"Arguments are invalid")?;
            Ok(())
        }
    } else {
        handle.write_all(b"No arguments have been provided.")?;
        Ok(())
    }
}

// fn pass(json: Value) {
//     fs::write("data/pass.json", serde_json::to_string_pretty(&json).unwrap()).unwrap();
// }

fn mcping(addr: &str, port: u16) -> bool {
    let ip = format!("{addr}:{port}");
        
    if let Ok(mut stream) = TcpStream::connect(ip) {
        let _pong = ping(&mut stream, addr, port).expect("Cannot ping server");
        return true
    } else {
        return false
    }
}
