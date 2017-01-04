package ronin;

import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.SwingConstants;
import java.awt.Dimension;

public class Frame extends JFrame {
	Frame() {
		super("HelloWorldSwing");
	    final JLabel label = new JLabel("Hello World", SwingConstants.CENTER);
	    this.getContentPane().add(label);
	    this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
	    this.setPreferredSize(new Dimension(400, 200));
	    this.pack();
	}
}