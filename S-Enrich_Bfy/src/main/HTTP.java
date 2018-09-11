//################################################################################
//##              Laboratory of Computational Intelligence (LABIC)              ##
//##             --------------------------------------------------             ##
//##       Originally developed by: João Antunes  (joao8tunes@gmail.com)        ##
//##       Laboratory: labic.icmc.usp.br    Personal: joaoantunes.esy.es        ##
//##                                                                            ##
//##   "Não há nada mais trabalhoso do que viver sem trabalhar". Seu Madruga    ##
//################################################################################

//URL: https://github.com/joao8tunes/S-Enrich

//Example usage: java -jar S-Enrich_Babelfy.jar EN in/db/ out/word/ out/id/

package main;

import java.io.IOException;
import java.net.URL;
import java.net.URLConnection;

public class HTTP
{

	public static boolean checkConnection() throws Exception
	{
		try {
			URL url = new URL("http://www.google.com.br");
			URLConnection connection = url.openConnection();
			connection.connect();
			return true;
		}
		catch (IOException e) {}

		return false;
	}

}