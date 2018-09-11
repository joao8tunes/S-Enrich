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

class UnlikelyException extends RuntimeException
{

	private static final long serialVersionUID = -8541507990752582195L;

	public UnlikelyException (Exception e)
	{
        super (e);
    }

}