default: bin/p3test.86p bin/p2test.86p

clean:
	rm -rf bin

bin/p3test.rel: test.c
	@mkdir -p $(dir $@)
	sdcc --compile-only -mz80 --nostdlib --no-std-crt0 --reserve-regs-iy --opt-code-speed --max-allocs-per-node 300 $^ -o $@

bin/p3test.ihx: bin/p3test.rel
	@mkdir -p $(dir $@)
	sdldz80 -m -w -x -i -b _CODE=0xD748 -b _DATA=0x0000 $@ $^

bin/p3test.bin: bin/p3test.ihx
	python3 ../ihxtobin.py $^
	python3 ../trim.py bin/p3test.map bin/p3test.bin 0xD748

bin/p3test.86p: bin/p3test.bin
	python3 ../binto86p.py 86 bin/p3test.bin $@
	rm p3test.86p

bin/p2test.rel: test.c
	@mkdir -p $(dir $@)
	sdcc --compile-only -mz80 --nostdlib --no-std-crt0 --reserve-regs-iy --opt-code-speed --max-allocs-per-node 300 $^ -o $@

bin/p2test.ihx: bin/p2test.rel
	@mkdir -p $(dir $@)
	sdldz80 -m -w -x -i -b _CODE=0xD748 -b _DATA=0x0000 $@ $^

bin/p2test.bin: bin/p2test.ihx
	python2 ../ihxtobin.py $^
	python2 ../trim.py bin/p2test.map bin/p2test.bin 0xD748

bin/p2test.86p: bin/p2test.bin
	python2 ../binto86p.py 86 bin/p2test.bin $@
	rm p2test.86p
