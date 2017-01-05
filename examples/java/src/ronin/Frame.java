package ronin;

import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.SwingConstants;
import java.awt.Dimension;
import java.awt.Toolkit;

public class Frame extends JFrame {
	Frame() {
		super("HelloWorldSwing");

		this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

		final JLabel label = new JLabel("Hello World", SwingConstants.CENTER);
		this.getContentPane().add(label);
		
		this.setPreferredSize(new Dimension(400, 200));
		this.pack();
		
		Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
		int x = (int) ((screenSize.getWidth() - this.getWidth()) / 2);
		int y = (int) ((screenSize.getHeight() - this.getHeight()) / 2);
		this.setLocation(x, y);
	}
}