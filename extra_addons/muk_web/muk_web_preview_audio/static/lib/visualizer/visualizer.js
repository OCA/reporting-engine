/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU Lesser General Public License as published by
*    the Free Software Foundation, either version 3 of the License, or
*    (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU Lesser General Public License for more details.
*
*    You should have received a copy of the GNU Lesser General Public License
*    along with this program. If not, see <http://www.gnu.org/licenses/>.
*
**********************************************************************************/

window.AudioContext = window.AudioContext || window.webkitAudioContext || window.mozAudioContext;

function Visualizer($audio, $container, $canvas) {
	var _this = this;
	
	this.$audio = $audio;
	this.$container = $container;
	this.$canvas = $canvas;
	
	this.audio = $audio.get(0);
	this.canvas = $canvas.get(0);
    
	this.audioCtx = new AudioContext();
	this.analyser = this.audioCtx.createAnalyser();
	this.audioSrc = this.audioCtx.createMediaElementSource(this.audio);
	this.frequencyData = new Uint8Array(this.analyser.frequencyBinCount);
	this.smoothEndingCounter = 0;
	
	this.audioSrc.connect(this.analyser);
	this.analyser.connect(this.audioCtx.destination); 
    
	this.ctx = this.canvas.getContext('2d'),
    
	this.capYPositionArray = [];
    
    this.$audio.bind('play', function (e) {
    	_this.smoothEndingCounter = 0;
    	_this.calcCanvas();
    	_this.renderFrame();
    });
    
    this.map = function (num, in_min, in_max, out_min, out_max) {
    	return (num - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
	}
    
	this.calcCanvas = function() {
		_this.canvas.width = _this.$container.width() !== 0 ? _this.$container.width() : 200;
		_this.canvas.height = _this.$container.height() !== 0 ? _this.$container.height() : 100;
		_this.cwidth = _this.canvas.width;
		_this.cheight = _this.canvas.height - 4;
		_this.meterWidth = 10;
		_this.capHeight = 4;
		_this.capStyle = '#FFF';
		_this.meterNum = (_this.$container.width() !== 0 ? _this.$container.width() : 650) / (10 + 2);
		
		_this.gradient = _this.ctx.createLinearGradient(0, 0, 0, _this.cheight);
		_this.gradient.addColorStop(1, '#1CD5FB');
		_this.gradient.addColorStop(0.75, '#19DECA');
		_this.gradient.addColorStop(0.5, '#28F5A6');
		_this.gradient.addColorStop(0.25, '#19DE5A');
		_this.gradient.addColorStop(0, '#1CFB27');
	}
    
	this.renderFrame = function() {
		if(_this.$container.width() !== _this.cwidth) {
    		_this.calcCanvas();
    	}

        _this.ctx.clearRect(0, 0, _this.cwidth, _this.cheight);

    	_this.analyser.getByteFrequencyData(_this.frequencyData);
        var step = Math.round(_this.frequencyData.length / _this.meterNum);
        
        for (var i = 0; i < _this.meterNum; i++) {
            var valueBar = _this.map(_this.frequencyData[i * step], 0, 255, 0, _this.cheight);
            var valueCap = _this.map(_this.frequencyData[i * step], 0, 255, 0, _this.canvas.height);
            
            if (_this.capYPositionArray.length < Math.round(_this.meterNum)) {
            	_this.capYPositionArray.push(valueCap);
            };
            
            _this.ctx.fillStyle = _this.gradient;
            _this.ctx.fillRect(i * 12, _this.cheight - valueBar, _this.meterWidth, _this.cheight);
            
            _this.ctx.fillStyle = _this.capStyle;
            if (valueCap < _this.capYPositionArray[i]) {
            	_this.ctx.fillRect(i * 12, _this.canvas.height - (--_this.capYPositionArray[i]), _this.meterWidth, _this.capHeight);
            } else {
            	_this.ctx.fillRect(i * 12, _this.canvas.height - valueCap, _this.meterWidth, _this.capHeight);
                _this.capYPositionArray[i] = valueCap;
            };
        }
        
        if(!_this.audio.paused) {
        	requestAnimationFrame(_this.renderFrame);
        } else {
        	if(_this.smoothEndingCounter < 500) {
        		requestAnimationFrame(_this.renderFrame);
        	}
        	_this.smoothEndingCounter++;
        }
    }
};
