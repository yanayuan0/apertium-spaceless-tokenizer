CXX      = g++
CXXFLAGS = -std=c++17 -O2

tokeniser: tokeniser.cpp
	$(CXX) $(CXXFLAGS) $< -o $@

clean:
	rm -f tokeniser

.PHONY: clean
