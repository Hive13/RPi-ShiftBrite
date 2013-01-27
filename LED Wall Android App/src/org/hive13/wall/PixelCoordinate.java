package org.hive13.wall;

// This class is just a holder for a pixel coordinate.
public class PixelCoordinate implements Comparable<PixelCoordinate> {

	public int x;
	public int y;
	
	public PixelCoordinate(int x, int y) {
		this.x = x;
		this.y = y;
	}

	@Override
	public int compareTo(PixelCoordinate other) {
		if (this.x == other.x && this.y == other.y) {
			return 0;
		} else if (this.x < other.x || (this.x == other.x && this.y < other.y)) {
			return -1;
		} else {
			return 1;
		}
	}
	
	@Override
	public int hashCode() {
		// auto-generated from Eclipse
		final int prime = 31;
		int result = 1;
		result = prime * result + x;
		result = prime * result + y;
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		// auto-generated from Eclipse
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		PixelCoordinate other = (PixelCoordinate) obj;
		if (x != other.x)
			return false;
		if (y != other.y)
			return false;
		return true;
	}
	
}
