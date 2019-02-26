import gate.*;
import gate.Utils;
import java.util.Set;
import java.util.HashSet;
import java.util.List;

// for each Knowmak annotation, find the underlying sequence of tokens
// and space tokens and use it to create the lemma string

private Set<String> TKSPTKTYPES = new HashSet<String>();

@Override
public void init() {  
  TKSPTKTYPES.add("Token");
  TKSPTKTYPES.add("SpaceToken");
}


@Override
public void execute() {
  AnnotationSet anns = inputAS.get("Knowmak");
  AnnotationSet tksptk = inputAS.get(TKSPTKTYPES);
  for(Annotation ann : anns) {    
      // get all the tokens and space tokens in document order
      List<Annotation> tsanns = 
        gate.Utils.getContainedAnnotations(tksptk,ann).inDocumentOrder();
      StringBuilder sb = new StringBuilder();
      for (Annotation tsann : tsanns) {
        if(tsann.getType().equals("Token")) {
          sb.append(tsann.getFeatures().get("root"));        
        } else {
          sb.append(" ");
        }
      }
      ann.getFeatures().put("root",sb.toString());
  }
}
