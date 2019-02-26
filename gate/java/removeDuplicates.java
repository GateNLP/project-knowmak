// Remote duplicate annotations

import gate.*;
import java.util.*;

@Override
public void execute() {

  String anntype = (String)parms.get("annotationType");
  Set<Annotation> toRemove = new HashSet<Annotation>();

  // we use the following trick to remove annotations from a document that
  // is assumed to be of limited length: store the range as fromOffset+(X*toOffset)
  // where X is chosen big enough to not interfere with fromOffset but small enough
  // to not let the product overflow. We assume a maximum size of the document to be less than
  // a gigabyte or 2^30, then the largest number we can get is (2^30-1)+(2^30*(2^30-1))
  // or 1152921504606846975 which is way smaller than 2^63 or 9223372036854775808
  Set<Long> offsets = new HashSet<Long>();
  Long X = 1073741824L;
  for(Annotation ann : inputAS.get(anntype)) {
    Long from = gate.Utils.start(ann);
    Long to = gate.Utils.end(ann);
    Long xtest = from + X*to;
    if(offsets.contains(xtest)) {
      toRemove.add(ann);
    } else {
      offsets.add(xtest);      
    }
  }
  
  inputAS.removeAll(toRemove);
}
