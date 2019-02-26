import gate.*;
import java.io.*;
import java.util.*;
import gate.util.*;

@Override
public void execute() {  
  // for each document open the output file based on the document name
  // the document name could contain a full relative path of the form
  // dir1/dir2/filename.ext and for now we expect that all those directories
  // in the tree get created beforehand and already exist!
  String docName = doc.getName();
  // if there is a silly GATE random code at the end of the name, remove
  docName = docName.replaceAll("_[0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F]$","");
  // remove the (last) extension
  docName = docName.replaceAll("\\.[a-zA-Z]+$","");
  // append the relative path to the output directory
  String outDir = (String)parms.get("outputDirectory");
  if(outDir==null) outDir = ".";
  // NOTE/TODO: this is non-portable and only works on *NIX-like OSs
  String outPath = outDir + "/" + docName + ".conll";

  // before we do the actual outputting, add a feature to each token that
  // is contained within a KNOWMAK annotation
  AnnotationSet tokens = inputAS.get("Token");
  AnnotationSet knowmaks = inputAS.get("Knowmak");
  for(Annotation knowmak : knowmaks) {
    AnnotationSet containedTokens = gate.Utils.getContainedAnnotations(tokens,knowmak);
    for(Annotation token : containedTokens) {
      token.getFeatures().put("withinKnowmak", 1);
    }
  }
  
  //System.err.println("DEBUG in thread "+duplicationId+": writing to "+outPath);
  // write to a UTF-8 writer to that file
  try (FileWriter fw = new FileWriter(outPath);
       BufferedWriter bw = new BufferedWriter(fw);
       PrintWriter pw = new PrintWriter(bw)) {
    // go through all the sentences
    for(Annotation sent : inputAS.get("Sentence").inDocumentOrder()) {
      // go through all the tokens inside the sentence
      for(Annotation tok : gate.Utils.getContainedAnnotations(tokens,sent).inDocumentOrder()) {
        String txt = gate.Utils.cleanStringFor(doc, tok);
        String root = (String)tok.getFeatures().get("root");
        String pos = (String)tok.getFeatures().get("category");
        Object withinKnowmak = tok.getFeatures().get("withinKnowmak");
        pw.print(txt);
        pw.print("\t");
        pw.print(root);
        pw.print("\t");
        pw.print(pos);
        pw.print("\t");
        if(withinKnowmak == null) {
          pw.print("0");
        } else {
          pw.print("1");
        }
        pw.println();
      }
      pw.println();
    }
  } catch (Exception ex) {
    System.err.println("ERROR: problem writing document "+doc.getName()+" to "+outPath);
    ex.printStackTrace(System.err);
    throw new GateRuntimeException("Could not export document "+doc.getName(),ex);
  }
  
}
