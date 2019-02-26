import gate.*;
import gate.Utils;
import java.util.List;

// Go through all the TokenSeq annotations we found and get the contained
// Token annotations in order. Find out if at least one of them is of kind word.
// If yes, create a new Token annotation with the following features:
// category: same as from first contained word token
// kind: word
// length: length of TokenSeq annotation
// root: concatenation of all root features of all contained token annotations
// string: concatenation of all string features of all contained token annotations

@Override
public void execute() {
  AnnotationSet tokens = inputAS.get("Token");
  AnnotationSet tokenseqs = inputAS.get("TokenSeq");
  for(Annotation tokenseq : tokenseqs) {
    List<Annotation> tokenlist = gate.Utils.getContainedAnnotations(tokens, tokenseq).inDocumentOrder();
    String category = null;
    for(Annotation token : tokenlist) {
      String kind = (String)token.getFeatures().get("kind");
      if(kind.equals("word")) {
        category = (String)token.getFeatures().get("category");
        break;
      }
    }
    // if we have category set, this is an indicator that we want to convert
    if(category!=null) {
      String roots[] = new String[tokenlist.size()];
      String strings[] = new String[tokenlist.size()];
      int i = 0;
      for(Annotation token : tokenlist) {
        roots[i] = (String)token.getFeatures().get("root");
        strings[i] = (String)token.getFeatures().get("string");
        i++;
      }
      FeatureMap fm = Factory.newFeatureMap();
      fm.put("fromseq",true);
      fm.put("length", gate.Utils.length(tokenseq));
      fm.put("category", category);
      fm.put("root", String.join("",roots));
      fm.put("string", String.join("",strings));
      // calculate all the other features
      // add a new Token annotation
      gate.Utils.addAnn(outputAS, tokenseq, "Token", fm);
      // remove the contained Token annotations
      inputAS.removeAll(tokenlist);      
    }
  }
}
