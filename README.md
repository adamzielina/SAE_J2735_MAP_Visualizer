# SAE_J2735_MAP_Visualizer

This repo is a tool developed for my work purposes. I was using Cohda MK6C to gather V2X data frames from the intersections around the state of Maryland. I was logging data on the device but I wanted to check the results in real time, so I could tell during sniffing whether intersection broadcasts proper message or not. I was using wireshark at the beggining to do that but it wasn't perfect for my needs. I could see all the fields with values but it doesn't tell you instantly if the message is correct. When you have localization and intersection geometry written in numerical values it's not possible to tell how it looks just from looking at it. So I created this tool to receive V2X data frames, extract and decode SAE J2735 message sublayer and most importantly display it's content in a visualized way on a web map. 

It implements j2735 decoding tool by USDOT. Which uses pycrate to decode to asn.1 structure. see below for more details.   
[j2735decoder](https://github.com/usdot-fhwa-stol/j2735decoder)
