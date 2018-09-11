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

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.logging.Logger;

import it.uniroma1.lcl.babelfy.commons.annotation.SemanticAnnotation;
import it.uniroma1.lcl.babelfy.core.Babelfy;
import it.uniroma1.lcl.jlt.util.Language;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;

public class Main
{
    /* Default values
     * Annotation Resource 			BN
	 * Annotation Type 				ALL
	 * Disambiguation Constraint 	DISAMBIGUATE_ALL
	 * Matching Type 				EXACT_MATCHING
	 * MCS Type 					ON
	 * PoS tagging Options 			STANDARD
	 * Scored Candidates 			TOP
	 * Threshold 					0.7
	 * Multi-token expression		true
     */
	public static char CH_BREAKLINE = "\n".toCharArray()[0];
	public static char CH_SPACE = " ".toCharArray()[0];
	public static int MAX_CHARS = 10000;

	public static Object[] babelfyRequest(String text, Language language)
	{
		ArrayList<List<SemanticAnnotation>> r = new ArrayList<>();
		Babelfy bfy = new Babelfy();
		int waitTime[] = new int[]{0};

		do {
			try {
				if (HTTP.checkConnection()) {
					ExecutorService executor = Executors.newFixedThreadPool(4);

					Future<?> future = executor.submit(new Runnable()
					{
					    @Override
					    public void run()
					    {
					    	List<SemanticAnnotation> bfyAnnotations = null;

							try {
								bfyAnnotations = bfy.babelfy(text, language);
							}
							catch (Exception e) {
								throw new UnlikelyException(e);
							}

							if (bfyAnnotations != null) r.add(bfyAnnotations);
							else {
								try {
									TimeUnit.MINUTES.sleep(5);    //Wait 5 minutes before do another request to Babelfy service (server).
									waitTime[0] += 60*5;
								}
								catch (InterruptedException e) {}
							}
					    }
					});

					executor.shutdown();    //Reject all further submissions.

					try {
					    future.get(5, TimeUnit.MINUTES);  //Wait 5 minutes to finish request (the Babelfy API response is obtained in less than 5 seconds for the maximum string (10k characters)).
					}
					catch (InterruptedException e) {}    //Possible error cases (interrupted).
					catch (ExecutionException e) {}    //Caught exception.
					catch (TimeoutException e) {
					    future.cancel(true);    //Interrupt the job (timeout).
					    waitTime[0] += 60*5;
					}

					if (!executor.awaitTermination(2, TimeUnit.SECONDS)) {    //Wait all unfinished tasks for 2 sec.
					    executor.shutdownNow();    //Force them to quit by interrupting.
					    waitTime[0] += 2;
					}
				}
				else {
					TimeUnit.SECONDS.sleep(5);
					waitTime[0] += 5;
				}
			}
			catch (Exception e) {}
		} while (r.isEmpty());

		return new Object[]{r.get(0), waitTime[0]};
	}

	@SuppressWarnings("unchecked")
	public static void main(String args[]) throws IOException, InterruptedException
	{
		Logger logger = Logger.getLogger("");    //Disable JAVA log (messages).
		ArgumentParser parser = ArgumentParsers.newArgumentParser("Disambiguation").defaultHelp(true).description("Semantic enriching raw text.");
		Language language = null;
		int waitTime = 0;

		logger.removeHandler(logger.getHandlers()[0]);    //Disable JAVA log (messages).
		parser.addArgument("language").nargs(1).help("Specify text language.");
		parser.addArgument("input").nargs(1).help("Input raw text file.");
		parser.addArgument("output").nargs(2).help("Output enriched text files ('word' and 'id').");
		Namespace ns = null;

        try {
            ns = parser.parseArgs(args);
        }
        catch (ArgumentParserException e) {
            parser.handleError(e);
            System.exit(1);
        }

        String idiom = ns.getString("language").substring(1, ns.getString("language").length()-1);
        String input = ns.getString("input").substring(1, ns.getString("input").length()-1);
        String[] files = ns.getString("output").substring(1, ns.getString("output").length()-1).split(",");
		String output_word = files[0].trim();
		String output_id = files[1].trim();

		switch (idiom) {
			case "ES": {    //Spanish.
				language = Language.ES;
			} break;
			case "FR": {    //French.
				language = Language.FR;
			} break;
			case "DE": {    //Deutsch.
				language = Language.DE;
			} break;
			case "IT": {    //Italian.
				language = Language.IT;
			} break;
			case "PT": {    //Portuguese.
				language = Language.PT;
			} break;
			default: {      //English.
				language = Language.EN;
			}
		}

		List<SemanticAnnotation> bfyAnnotations = null;
		BufferedReader br = new BufferedReader(new FileReader(new File(input)));
		BufferedWriter bw_word = new BufferedWriter(new FileWriter(new File(output_word)));
		BufferedWriter bw_id = new BufferedWriter(new FileWriter(new File(output_id)));
		String inputText = "";
		int requests = 0;
		int startFragment = 0, endFragment = MAX_CHARS-1, maxFragment = 0;
		boolean flushBreakLine = false, AUX = true;

		while (br.ready()) {
			inputText += br.readLine() + "\n";
		}

		br.close();
		maxFragment = inputText.length();

		while (startFragment < maxFragment) {
			if (maxFragment-startFragment <= MAX_CHARS) endFragment = maxFragment;

			++requests;
			String fragment = inputText.substring(startFragment, endFragment);
			char[] fragmentChars = fragment.toCharArray();
			int returnChar = 0, len_fragmentChars = fragmentChars.length, curBreakLineIndex = 0;

			if (endFragment < maxFragment) {
				if (!fragment.endsWith(String.valueOf(CH_BREAKLINE))) {
					while (fragmentChars[len_fragmentChars-returnChar-1] != CH_BREAKLINE) {
						++returnChar;

						if (returnChar >= len_fragmentChars) {
							returnChar = 0;
							break;
						}
					}
				}

				if (returnChar == 0 && !fragment.endsWith(String.valueOf(CH_SPACE))) {
					while (fragmentChars[len_fragmentChars-returnChar-1] != CH_SPACE) {
						++returnChar;

						if (returnChar >= len_fragmentChars) {
							returnChar = 0;
							break;
						}
					}
				}
			}

			endFragment -= returnChar;
			fragment = inputText.substring(startFragment, endFragment);
			fragmentChars = fragment.toCharArray();
			len_fragmentChars = fragmentChars.length;
			Object[] response = babelfyRequest(fragment, language);
			bfyAnnotations = (List<SemanticAnnotation>) response[0];
			waitTime += (int) response[1];

			if (!bfyAnnotations.isEmpty()) {
				if (flushBreakLine) {
					++curBreakLineIndex;
					flushBreakLine = false;
				}

				ArrayList<Integer> breakLines = new ArrayList<Integer>();
				int endOffset = bfyAnnotations.get(0).getCharOffsetFragment().getEnd();
				int annotation_i = 0, len_annotations = bfyAnnotations.size(), len_breakLines;
				String maxOffsetWord = "", maxOffsetId = "";

				for (int char_i = 0; char_i < len_fragmentChars; ++char_i) {
					if (fragmentChars[char_i] == CH_BREAKLINE) breakLines.add(char_i);
				}

				len_breakLines = breakLines.size()-1;

				for (SemanticAnnotation annotation : bfyAnnotations)
				{
					//Splitting the input text using the CharOffsetFragment start and end anchors:
					String fragWord = fragment.substring(annotation.getCharOffsetFragment().getStart(), annotation.getCharOffsetFragment().getEnd()+1).trim().replaceAll(" ", "_");
					String fragId = annotation.getBabelSynsetID();

					if (annotation.getCharOffsetFragment().getStart() <= endOffset) {
						if (fragWord.length() > maxOffsetWord.length()) {
							maxOffsetWord = fragWord;
							maxOffsetId = fragId;
							endOffset = annotation.getCharOffsetFragment().getEnd();
						}
					}
					else {
						if (!breakLines.isEmpty() && annotation.getCharOffsetFragment().getEnd() >= breakLines.get(curBreakLineIndex)) {
							int newCurBreakLineIndex = curBreakLineIndex;

							AUX = true;

							while (newCurBreakLineIndex < len_breakLines && annotation.getCharOffsetFragment().getEnd() >= breakLines.get(newCurBreakLineIndex)) ++newCurBreakLineIndex;

							if (newCurBreakLineIndex-curBreakLineIndex == 1) ++curBreakLineIndex;
							else curBreakLineIndex = newCurBreakLineIndex;    //Possible lines without any NE or concept.

							bw_word.write(maxOffsetWord + "\n");
							bw_id.write(maxOffsetId + "\n");
						}
						else {
							if (breakLines.isEmpty()) AUX = false;

							bw_word.write(maxOffsetWord + " ");
							bw_id.write(maxOffsetId + " ");
						}

						endOffset = annotation.getCharOffsetFragment().getEnd();
						maxOffsetWord = fragWord;
						maxOffsetId = fragId;
					}

					++annotation_i;

					if (annotation_i >= len_annotations) {
						bw_word.write(maxOffsetWord + " ");
						bw_id.write(maxOffsetId + " ");
					}
				}

				startFragment = endFragment;
				endFragment = startFragment+MAX_CHARS;

				if (startFragment < maxFragment && AUX) {
					++curBreakLineIndex;
					bw_word.write("\n");
					bw_id.write("\n");
				}
			}
			else {
				int breaks = 0;

				if (!flushBreakLine) flushBreakLine = true;

				for (int char_i = 0; char_i < len_fragmentChars; ++char_i) {
					if (fragmentChars[char_i] == CH_BREAKLINE) ++breaks;
				}

				startFragment = endFragment;
				endFragment = startFragment+MAX_CHARS;

				if (startFragment < maxFragment) {
					curBreakLineIndex += breaks;
				}
			}
		}

		bw_word.close();
		bw_id.close();
		System.out.print(requests + " " + waitTime);
	}

}