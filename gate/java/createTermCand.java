import gate.*;
import gate.Utils;
import java.util.Set;
import java.util.HashSet;
import java.util.List;

// Create TermCand annotations from the termraider SingleWord and MultiWord
// annotations but also from everything that was detected as a Knowmak 
// annotation.

private Set<String> TKSPTKTYPES = new HashSet<String>();

@Override
public void init() {  
  TKSPTKTYPES.add("Token");
  TKSPTKTYPES.add("SpaceToken");
}


@Override
public void execute() {
  AnnotationSet anns = inputAS.get("SingleWord");
  AnnotationSet tksptk = inputAS.get(TKSPTKTYPES);
  for(Annotation ann : anns) {
    gate.Utils.addAnn(
      outputAS, ann, "TermCand", gate.Utils.toFeatureMap(ann.getFeatures()));
  }
  anns = inputAS.get("MultiWord");
  for(Annotation ann : anns) {
    // calculate the canonical feature unless we already have one
    String canonical = (String)ann.getFeatures().get("canonical");
    if(canonical==null) {
      // get all the tokens and space tokens in document order
      List<Annotation> tsanns = 
        gate.Utils.getContainedAnnotations(tksptk,ann).inDocumentOrder();
      StringBuilder sb = new StringBuilder();
      for (Annotation tsann : tsanns) {
        if(tsann.getType().equals("Token")) {
          sb.append(tsann.getFeatures().get("canonical"));        
        } else {
          sb.append(" ");
        }
      }
    }
    gate.Utils.addAnn(
      outputAS, ann, "TermCand", gate.Utils.toFeatureMap(ann.getFeatures()));
  }
  AnnotationSet termcands = outputAS.get("TermCand");
  anns = inputAS.get("Knowmak");
  for(Annotation ann : anns) {
    //System.err.println("DEBUG: checking knowmak ann "+ann);
    // only add unless the same span is not already added
    AnnotationSet coexts = gate.Utils.getCoextensiveAnnotations(termcands, ann);
    if(coexts.isEmpty()) {      
      FeatureMap fm = Factory.newFeatureMap();
      fm.put("canonical", (String)ann.getFeatures().get("match"));
      gate.Utils.addAnn(
        outputAS, ann, "TermCand", gate.Utils.toFeatureMap(fm));
    }
  }

}
