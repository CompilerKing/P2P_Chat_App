# P2P_Chat_App
A Peer-to-Peer chat application developed for Comp 429 (Computer Networks) based on a class defined protocol.

**Authors:**  
 Sam Decanio  
 Philip Porter  
 Vlad Synnes

**Potential Problems with the protocol:**
- A client with no peers has an unset username even after receiving a join request
This means that the first person, from which all connections originate can't have 
a username.
- There is no need to specify a "listening port" when sending messages
such as the JOIN, CONNECT, etc... messages. These messages are sent over a TCP connection
that has already been established - there is no need for another connection on the "listening port".