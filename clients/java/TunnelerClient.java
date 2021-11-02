/*
 * For more information about java-websockets, check out the github repo below:
 * https://github.com/TooTallNate/Java-WebSocket
 */

import java.net.URI;
import java.net.URISyntaxException;
import java.util.Map;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.drafts.Draft;
import org.java_websocket.handshake.ServerHandshake;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class TunnelerClient extends WebSocketClient {
	
	// Some constants
	public static String hostName = "127.0.0.1";
	public static int port = 8081;
	public static String clientName = "JavaClient";
	public static String stage = "params";
	public static long n, k, p;

	public TunnelerClient(URI serverUri, Draft draft) {
		super(serverUri, draft);
	}
	
	public TunnelerClient(URI serverURI) {
		super(serverURI);
	}
	
	public TunnelerClient(URI serverUri, Map<String, String> httpHeaders) {
		super(serverUri, httpHeaders);
	}
	
	 @Override
	 public void onOpen(ServerHandshake handshakedata) {
		JSONObject obj = new JSONObject(); 
		
		// Starting communication with the server once connection is opened
		obj.put("role", "Tunneler");
		obj.put("name", clientName);
		send(obj.toJSONString());
		
		System.out.println("opened connection");
	}
	
	@Override
	public void onMessage(String message)  {
		System.out.println("received: " + message);
		JSONObject obj = null;
		try {
			obj = (JSONObject) new JSONParser().parse(message);
		} catch (ParseException e) {
			e.printStackTrace();
		}
		// Two stages - parameter reception and tunneling
		if(stage == "params") {
			System.out.println("Parameters obtained: n - " + obj.get("n") + " k - " + obj.get("k") + " p - " + obj.get("p"));
			n = (long)obj.get("n");
			k = (long)obj.get("k");
			p = (long)obj.get("p");
			//Change stage to tunneling once params are received
			stage = "tunneling";
		} else if(stage == "tunneling") {
			
			// Place your code here
			
			try {
				// Sample send
				JSONObject retVal = (JSONObject)new JSONParser().parse("{\"name\": \"" + clientName + "\", \"edges\": [[[0, 0], [0, 1]], [[0, 1], [1, 1]], [[1, 1], [1, 2]], [[1, 2], [2, 2]], [[2, 2], [2, 3]]]}");
				send(retVal.toJSONString());
			} catch (ParseException e) {
				e.printStackTrace();
			}
		}
	}
	
	@Override
	public void onClose(int code, String reason, boolean remote) {
	System.out.println(
			"Connection closed by " + (remote ? "remote peer" : "us") + " Code: " + code + " Reason: " + reason);
	}
	
	@Override
	public void onError(Exception ex) {
		ex.printStackTrace();
	}
	
	public static void main(String[] args) throws URISyntaxException {
		TunnelerClient c = new TunnelerClient(new URI(
	        "ws://" + hostName + ":" + port));
	    c.connect();
	  }

}