"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8512669067e448a9b1d3fb78bf0c61c6/part_014.stl', 'relative_path': '8512669067e448a9b1d3fb78bf0c61c6/part_014.stl', 'source_sha256': 'af2b1ed14f555440ae903008ec6366f952f51cd30e9bc66234908ad79582f8a9', 'input_faces': 192, 'input_vertices': 136, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09430335462093353, -0.07896894216537476, -0.1412292718887329], [0.12857455015182495, 0.29576510190963745, 0.017740465700626373]]}
GEOMETRY_BASE85 = 'c$}q}2~ZSQ8pj(!0TD$Zibk;wDjvjmAYMe;D?tzhj2bXVqYf~rpj-wNrV%_M1{1MVvQbAtcRleW9x-;jR@b8xjnUoG9XD#$jj61<9;tP++wc4SZDvxtRa?7L_0|8^f8M<J`s>&4eM5YVyGMY;pDxmxg5DL1uOx|RAq7Z<mfU>nbW2{J>^Vhlk{|ivV`_EW#Mt;GH>psXA2P#|H$69Gs2mcJJ~$*)4oT0+&CgBCPR+@kVG;gYX|wVyhM$+2HpgOI_vkkuJX9XgGgK~-|Hn^rV+#7Ht_P19>hO4eDpJhpWZOOB+74fTP<dAPO81=KP`gR>pOK~|UKGAo{fEusTKjq@`Sxbt9T&d+%He(DT1~Q(uYX;6PWbAx@>*)QBB?>BGVr5I!q+?Or~b7w?gvP>1s$V)N{;TO?^`4GlfN-~AN6zFvYWoYa0`v&=(X|$wck)p^KsO)CtvfveTe4y`6#+CwbnuXNp+D8)X$}J)Q=igM84J`kNVeY+}2V5rvkWrRLUy4PMG~`q4Jrg?BBY+n&$US>LD7p@dS+{U4K$R{b~C+k5`VeU+=Yx#{Ho+jjO41*|&dCNcs2mt*3q*IqWaJPrjquWzJ(-Ci{V<^J(6zZf>XRyYG;%1umz&=_e1=kzcCs=6-H3ruMDlk5K<@M)3I6n<x+R(jYtaAH9*rm#R)u-sG9*+0Q<`i~N0m*-82F9sLRUw(0DzwUpAeXIFZ@N=v`(&hytd-9O6nzPQcVS4&d3|L}I?YljA1ru)6sp60I%|8^^_mmB50-lEk?`u^w><jaY>XkAJ2>S5IG`NGZYhnyte{&qHvv;NbK<QEUn$zM7$iTc?!hJ5{WW+SbiM;^Q`k36J#NxSFJe6%NPXgvM5wd^;)LF+`?5tK{U587{_`Ckn>LhYyC<mdnFoAop=rHcDsw%`luXWZ{UrROlKocmvUhVzxQmVA4}UCu-KI({E2lYd2jw{HB5+Lweaqj}aZpywc!`_|KZ^x#CgK6kH%`WbzI`q6!6^7=mOsBzA}<iqPiy4=A2)VtNBt*$QTbrtX0-u;43^Z)D9wdBt!r1wE8`|x9$&yUyHFB;5wjoQxbJ#Fka@#N<m)I;a@?J0dvk`jYS_co(^D)2R5eK$YfQF)|)`)CFAx7bSglumWxb@h;a^>-`jeig4iypCtC<NL4|&^pjOnw3$%S@7eR%;3DKLnEDhtydc!SIg)??acN$i#X52>dL77q3`KA=p8pVI_F2~(Rm?hUq2i9eoqtWIfTH!_2(Vr=S69xS-0oX{EzIUew5pV$EclrCy=hI=JRv>DUH^ll2l(r-<x!i+N&SWqj4Qy6|5wG%?DfP`xpF=yZHK^0-AT@qc7?2*VuO)YT$A2XOb_&m-;`T_gntrJKfpWFMZ$0>+lC2*K9w25bx8|vS>e4uCuTGv61)V;$oVY3SVE5OZR0zd4%3~9lqmB55C{8Hqg3vz*m;sq4Pp%IfnP+8yNRWFuy;U7m8f`v+b$9w79E{#x?!$tNh-0J$X0M*_YO&llCp2=+Yi}lho`ex*yZmmhk)LH`e0f&#dKjvUbD*7hj(8Iq99j=`Q}0TNg-|&ZBi|H+>}`iF9N_sf+KB=aZ)G*IfL-GG4d6pDm&Mnf~J}UT=Qut6cm=9z4%$Kdx~0^^8rtPgdNkbnz>G;{En?@-li(@YNGG+HbY0UUY50W?S#PJ~gaQ-D2J3yq=YR@_Kf-@2#VLu>Liyf4%k}Tljh4J(Bo6a+tpP9?j+VNE_X6E6o${qk{KQ30p`0%YDF;_W{-P&3!=OeZcg8-UqC-4`^n4a~~MQ`+)90c^fJAB^CRU7Qnu_FUj7#FFEeb-p==feeW>ud(yY;zufl%dEb+h4^Z7;?w`83e<uEkeeAc=Sl(~#2@lyf_vdonpY^C9o;UV$Ge6ph1oo33^8O#G(>bdQPj_iAwc_)_5n(0YJYSR+e7@*zX*6&1{L(7;{8DUl$v4kCdkvp=^8Lr$9_OP{$>*aKy>}0dhx1o|%IB|k{3iM4d96I=^ID4V-b;Bh&-a5k->om`oPJpkEaiH@Ue%H79<zRMaQ&cF_G#ev3H3$-*BhGW81l{f#O^?S@_b{1bADtS*E7na<1W5l%k_`av*aM(S5vB&G@n4Km*fw-Q@tg%Jk532Y_7Xh>)+Wo>$f&sze%xM57YezuHbs_G}n9T`E7??o>vIhjq11^?4!<<TXCJKoZrd598UG5RCAG@i~goN)iKhl8XnhnjOtirpTfRb_uk>USKTw7ebmX?1g?{%tQWN3*|$|weJ*X{`dogolICsJ|4JvW|Ml7odVczv<@8+aIXdM*>rz0z`MX0|ZT#+tclq^I?Nj%L<}FHoN%A&+eWj;4{qz#1_?Y_de|lNN{=1)EL;C-}KfSsebLcAaU_>_~1{l#3+!Mag?%>%*%rGJcnheeXzXcrw?gov3jsbUrit)0I$Tea*#_5kabp;QG4g(8)6FeBKKu3awCV>_3ROl4&6pT3)A$Sfn7n}p04b28mGh(6<DG0&uAOsJE4gwDa4}lH@3rzqI0Vg5^zXw&pD#m^fngWhB!h*l6;Azlwu+RzMY2b;737D7Aeqf<}!Gpj9p|RkB-~^}&PC+i>phLlN;BbWCFz66)7&r!+2u{Sk#vlZzLQ}x0;529)I2}3x8V8QUJSHH*ao_#GeW79CzTjAB3^)d3$0AaZ`&5i)ahiwV3?nj)SO{GJ7Fq@ts(}}R%b~?!p)<kdU@J5lEHnyi1&>AuejOSO7TO#9I=BTi5G=F}xCPi3+7c`@04%f**cbeU5u>0Z5Q2w8`+$doBN2i_p#k7faC?N{*3g#V)?hzq8?Ya^12hmEh<omU5ZntPcpNku9F4q>LkOOQ5d1#07+j2J`94Ch4O#}aflHwaz@^|Kgy1Y_CO8Xh<}DMs6q@0b+YG1tXW*Fx88O+2P6)vrq4D63;IRn7h0w|1LT~{>a6UrtyU-x;Bxq-75V$SW9~uPq2YW#~fxW;U(2igaa1(^!rU=2WLdSw%1$RLRej6cpE<*4;Xd!qWco9PI5`^Hz&;syca0N6UTmddIVm>qvnh(xLzVe*%n1>KN9@-f^9vtkH-(ct~;9zhFLhx%)A8-$7JE#x19k>-juqX5tuqU`Vv@N(f*c<8(_69eDdV!mP-4TM#k6<^b2UutmaD0qglK}Vs^sn=uKbmOl@{jaie$%z=bN*(j(bvl&Fg~WKn6EK`CbV#dh)hZU0y=Hq(f'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
